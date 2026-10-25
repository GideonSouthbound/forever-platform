# 13 · Forever Logs API (the logging foundation for Module C)

**Status as of 2026-10-25** (operator, access process and the per-player limit added; first written 2026-10-24). Warcraft Logs has not added a Forever flavor (its flavor list still ends at Vanilla / SoD / Classic). A dedicated site, **Forever Logs** (foreverlogs.gg, "a Dao of Logging project"), has filled the gap and is already running rankings, guild profiles, speed-run boards and an armory off Phase 1 dungeon logs. It publishes a **versioned, documented, read-only REST API** — which is a better foundation than the GraphQL reverse-engineering the PoC was built around.

Treat it as the primary `logs` adapter and keep the Warcraft Logs client behind the same interface in case WCL ships a Forever host later.

**The limit that shapes the plan: without `events:read` there is no per-player data at all.** `/statistics` is aggregate only (percentile tables per class and spec). Per-player DPS, deaths, swings, uptimes, and attendance from a report all come from the event endpoints. The roadmap's decision point (`05-roadmap.md`) lists what to do if the scope is denied.

## Who runs it, and what that inherits

- **Operator:** The Dao of Logging, which also runs Triumvirate Logs and Frostmourne Logs, and the archived Ascension Logs: log sites for 3.3.5 private servers. Forever Logs is a tenant on that shared platform.
- **It is Blizzard's WoW: Forever.** Its public reports include beta runs of Forever-only dungeons (Ruins of Lordaeron, The Hall of Thanes, City of Dalaran, Excavation Site: Wetlands). It is not the 3.3.5 private server that also uses the word Forever (see the name-collision note in `11-dependency-status.md`).
- **Inherited text and defaults.** Parts of the FAQ describe 3.3.5 clients, and `/statistics` takes `difficulty` = `normal | heroic | mythic | ascended | all` with **default `ascended`**, a leftover from the Ascension tenant. Client rules: always pass `difficulty` explicitly (settle the right value on the first call by comparing `all` against `normal`); check what the `realm` filter means for a realmless game (ruleset or region) before using it; rely on no default.
- **Parser lineage.** The parser was built for 3.3.5 logs. Forever's client is retail-based (`WOW_PROJECT_ID = 1`), so its combat log is probably the modern format. The site evidently parses it (beta reports are live), but we have not verified field-level accuracy; the swing-count test in `06-acceptance-tests.md` checks it on our first recorded encounters.

## Getting access

1. Create an account, then a key in Profile Settings (https://foreverlogs.gg/profile). The full key is shown once: put it straight into the secret store.
2. `stats:read` is on every key. To get `events:read`, post the key's **visible prefix** (`alog_…`) and a short description of the project in the Forever Logs Discord (invite: https://foreverlogs.gg/discord; their FAQ points questions to its help channel). The process is described in their API docs, https://foreverlogs.gg/docs/api. They upgrade the existing key in place, so nothing changes in our config.
3. **Never share the full key with anyone, including them.** Their docs say the prefix is enough to identify it.
4. What our request says: a private, non-commercial guild tool; reads only the guild's own public reports after raid night; attendance and opt-in coaching notes visible only to the player and officers; no public rankings, no redistribution; attribution on every page that shows derived numbers; well under 1,000 requests a week; a private copy of our own raw events because retention is rolling (asking whether that is acceptable); and two questions, below (open questions 4 and 5).
5. Record the answer, with the date, in `11-dependency-status.md`.

## Contract

- **Base:** `https://foreverlogs.gg/api/public/v1` · OpenAPI 3.1 at `/openapi.json` (no key needed to read the spec) · version 1.0.0
- **Auth:** `Authorization: Bearer <key>` (or `X-API-Key`). **Keys in the query string are rejected.** Keys are created self-serve in Profile Settings and shown once.
- **Scopes:**
  - `stats:read` — self-serve, on every key. Aggregate statistics, phases, bosses.
  - `events:read` — **granted by hand to named projects**, marked experimental. Individual combat events, actors, report listings. This is the scope Module C's metric engine needs, so request it early and describe the project honestly (a private guild tool, not a public log site).
- **Rate limits, per key (not per IP):** free 30/min and 5,000/day (`stats:read`); partner 120/min and 50,000/day (`stats:read`); research 60/min and 10,000/day (`stats:read` + `events:read`). Event calls are deliberately slower per minute than partner because they do real database work.
- **Errors:** machine-readable codes — `missing_api_key`, `invalid_api_key`, `insufficient_scope`, `rate_limit_exceeded`, `daily_quota_exceeded`, `invalid_parameter`, `not_found`, `service_unavailable`. 429 carries `Retry-After`.
- **Terms:** visible attribution linking back is required wherever the data is displayed; bulk redistribution, or use as the basis of a competing combat-log service, is not permitted; keys that ignore this are revoked without notice. Our use (a private guild's own analysis, with attribution on every page that shows derived numbers) fits, but Module C must never republish their rankings wholesale.

## Endpoints

| Endpoint | Scope | What it gives us |
|---|---|---|
| `GET /statistics` | stats:read | Per class and spec: avg, median, max, min, total_parses and a **percentile table (p99…p10)**. Filters: `phase` (required), `difficulty`, `metric` (avg_dps / avg_hps / avg_dtps), `bracket` (raid size), `location`, `bossId`, `damageMode` (**standard / boss-only / trash**), `role`, `class`, `spec`, `weekNumber`, `realm`. Cacheable 30 min, carries an ETag. |
| `GET /phases` | stats:read | Content phases with start/end dates, `is_active`, and the `locations` in each (with `is_main`, `track_progression`, `is_world_boss`). |
| `GET /bosses` | stats:read | Boss metadata. **Index on `boss_id`, not `id`** — it is stable across zone recategorisation. |
| `GET /reports` | events:read | Newest public, fully-processed reports. `limit` (1–200), `offset`, `since`. |
| `GET /reports/{reportId}` | events:read | The report plus every encounter: id, name, boss_id, is_boss_encounter, start/end, duration_seconds. |
| `GET /reports/{id}/encounters/{eid}/events` | events:read | The event stream, keyset paged. |
| `GET /reports/{id}/encounters/{eid}/actors` | events:read | Actor dictionary: id → name, character_type (player/pet/creature), is_player, is_pet, is_boss. Fetch once per encounter. |
| `GET /health` | none | Liveness probe. |

## Event stream — the part that rewrites the metric engine

The `events` endpoint maps almost one-to-one onto `poc/metrics-spec.md`, and in several places it does work the PoC had to do by hand.

- **`timestamp_ms` is milliseconds from that encounter's combat start**, not wall clock. The spec's "times relative to fight start" is now native.
- **A swing is `event_type: "damage"` with `spell_id: -1`** (the melee sentinel, published on every response as `melee_spell_id` so it is not a magic number). **A swing that did not land is its own event type**: `parry`, `dodge`, `miss`, `block`, `deflect`, `immune`, `resist`, `reflect`, `evade`. Pairing the two gives a complete swing sequence with outcomes — exactly what swing-efficiency and parry-haste analysis need.
- **`melee_only=true`** narrows the stream to swing rows. Prefer it over filtering `spell_id = -1` yourself: a minority of genuine swings carry a real spell id (weapon imbues, some pet melee).
- **`is_glancing` / `is_crushing` are recorded going forward only** and are `null` on anything ingested before 2026-08-23. Null means *not recorded*, never *did not happen* — the metric engine must not treat null as evidence a mechanic is absent.
- **Filters:** `groups` (damage, healing, overheal, absorb, casts, buffs, debuffs, avoidance, interrupts, dispels, deaths), `event_types`, `source_ids`, `target_ids`, `spell_ids`, `start_ms`, `end_ms`.
- **Paging:** `limit` up to 50,000, cursor-based (`next_cursor` → `?cursor=`). **Cost is per request, not per row — prefer very large pages.** One call per encounter, not a hundred.

### Two footguns to encode in the client
1. **`id` and `amount` are 64-bit integers serialised as strings.** Parse `amount` before arithmetic or you will concatenate instead of add. Treat `id` as opaque; do not parse it as a number.
2. **`amount` means different things per event type** — damage/heal value, absorbed amount, aura stack count on a buff/debuff application, overkill on death. Switch on `event_type` before aggregating.

## What this changes in the build

- **PoC Job B (rankings sampling) mostly collapses.** `/statistics` already returns percentile tables per class/spec/boss/phase/bracket, cached and ETagged. One call replaces the page-walking. Reference *bands* for outcome metrics come from there; the per-metric bands (swing efficiency, uptimes, consumes, cooldown usage) still need the event stream, because those metrics do not exist in anyone's aggregate.
- **`damageMode=boss-only` solves the padding filter** that the PoC specified by hand.
- **Context scoring gets easier**: `bracket` and `weekNumber` are first-class filters, and so are `difficulty` and `realm`, with the caveats under "Who runs it".
- **Retention is a rolling window, not an archive.** An encounter readable today may age out. Our ingest must archive the guild's own raw events on first read (already the design: `raw_events` + object storage), and the close-out job becomes time-sensitive — pull within days, not months.
- **No combatant info.** The documented event groups (damage, healing, overheal, absorb, casts, buffs, debuffs, avoidance, interrupts, dispels, deaths) carry no gear or talents at the pull, which Warcraft Logs supplied. Gear sets therefore come from the armory if it is exposed (open question 3) or from a character-export paste; talents come from the member's saved build (Module F) or are inferred from casts and buffs. Whether buffs already present at the pull appear in the buff events is unverified; check it on the first recorded encounter before building consume checks on it.
- **No upload API.** Logs reach the site through its own uploader or the browser; the platform's close-out flow is "officer pastes a report id/URL → we fetch and ingest."
- **404 is returned identically for "does not exist" and "is not public,"** so private reports cannot be enumerated — and our ingest must tell members to upload publicly, or we cannot read it.
- **Experimental means the response shape may change without a version bump.** Pin nothing that cannot be re-run; the adapter's fixtures must be re-recorded whenever the shape moves.

## Open questions for the Forever Logs team
1. Can the guild get `events:read` (research tier)? Requested per "Getting access" above; the answer goes in `11-dependency-status.md`.
2. Is there any guild-scoped endpoint (the site has guild profiles and an armory) — i.e. "all reports for guild X" — or is listing public reports with `since` the only path to auto-attach?
3. Does the armory expose per-character gear, which would populate `gear_sets` without an addon export?
4. Retention window length, concretely, so the ingest cadence can be set against it. (Asked in the access request.)
5. May we build per-metric reference bands (swing efficiency, uptimes) from other guilds' public reports, for internal use only, or should bands come from our own reports plus `/statistics`? (Asked in the access request; until they say yes, bands come from our own history.)

## Appendix: the access request (draft, not yet sent)

Post in the Forever Logs Discord (https://foreverlogs.gg/discord). Replace `alog_XXXXXXXX` with the **visible prefix** of a key that has never been pasted anywhere, and fill in the community name.

```
Hi! I'd like to request `events:read` for a guild project.

Key prefix: `alog_XXXXXXXX`

**What it is:** a private, non-commercial tool for our WoW: Forever community, [Community name] (2–3 raid teams, Horde on RP-PvP). After raid night an officer pastes our report link, and the tool reads that report's encounters, actors and events to record attendance and write opt-in coaching notes for our own raiders (melee swing uptime, deaths, cooldown use). Notes are visible only to the player and our officers.

**What it isn't:** not a log site, no public rankings, no redistribution. Every page that shows numbers built from your data links back to Forever Logs.

**Load:** our own public reports only, about 3–6 a week starting Dec 9. Roughly one events call per encounter at large page sizes, cached so nothing is fetched twice. Well under 1,000 requests a week.

Because retention is rolling, we'd keep a private copy of our own guild's raw events so reviews can be re-run later. Let me know if that's not OK.

Two questions:
1. Would you be OK with us building comparison bands (e.g., typical swing uptime by spec) from other guilds' public reports, for internal use only? Or should we stick to our own reports plus /statistics?
2. Roughly how long is the event retention window?

Thanks for building this.
```
