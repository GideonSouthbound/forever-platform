# Naxx Parse-Review Proof of Concept — Build Brief

> **Status (25 Oct 2026): reference only, not Phase 0.** Warcraft Logs has no Forever flavor; Forever's logs come from Forever Logs (`../13-forever-logs-api.md`). Keep `metrics-spec.md` and the review templates as the authority for Module C's metric math and review text. The Warcraft Logs data layer here (`wcl-queries.graphql`, Job B sampling, Era report fixtures) is superseded. Build this folder only as an optional offline test of the math; the platform build starts at Phase 1 in `../05-roadmap.md`.

**Purpose:** prove the analytics pipeline behind a guild platform for WoW: Forever, using Classic Era data (which exists today) before Forever data exists (launch Nov 4, 2026). If this works on Era Naxxramas, the same code runs on Forever logs by changing config.

**What "working" means:** paste a Warcraft Logs report URL, pick a player and a Naxx boss, and get an automated parse review that (1) states what the player did, (2) compares it to reference bands built from public top-parse logs, (3) attributes the gap to the next band, (4) includes a melee swing-efficiency block, and (5) ends with a plain-language paragraph for casual players.

This file is the primary prompt. Supporting files: `wcl-queries.graphql`, `metrics-spec.md`, `schema.sql`, `boss-config.json`, `consumes.json`, `review-example.md`, `.env.example`.

---

## 1. Scope

**In scope**
- Warcraft Logs API v2 (GraphQL) client with OAuth client-credentials, rate-limit awareness, and response caching in Postgres.
- Three Classic Era Naxxramas bosses, chosen for distinct analysis flavors:
  - **Patchwerk** — single target, no movement: cleanest swing-efficiency test.
  - **Loatheb** — cooldown alignment with Fungal Bloom spore windows.
  - **Thaddius** — forced movement (Polarity Shift): tests gap classification.
- Two specs to start: **Fury Warrior** and **Combat Rogue** (melee, swing analysis). Hunter (Auto Shot) is a stretch goal.
- Reference bands (75–94, 95–98, 99+) per boss × spec × kill-time bucket, built from public ranked parses.
- Guild report ingest: any public report URL → fights → players → metrics → review.
- Boss lethality table from deaths (killing-blow ability) across ingested reports.
- A second data-source adapter as a pattern proof: snapshot poller for `https://talentsforever.com/data.json` (ETag-aware, versioned). Not used by the review; it proves the adapter/snapshot mechanism.
- Minimal web UI (5 pages, see §6).

**Out of scope (do not build)**
Discord bot, Raid-Helper, softres.it, multi-team, gear planner, simulators, strat animations, live logging, auth. No monetization of any kind.

---

## 2. Stack

- **Next.js (App Router) + TypeScript**, Tailwind for styling (keep it plain).
- **Postgres** (Replit's built-in) with **Drizzle ORM**; `schema.sql` is the reference DDL — translate to Drizzle schema, don't hand-write SQL in app code.
- Jobs run as **route handlers / server actions triggered by UI buttons** (no cron dependency in the PoC). Each job is idempotent and resumable: it records progress in `jobs` and skips work already cached.
- Raw API responses stored as **JSONB in Postgres**, never on disk (Replit filesystem is not durable).
- Tests: **Vitest**. The metric engine must be testable offline using recorded fixtures (see §7).
- No external services beyond Warcraft Logs and talentsforever.com.

---

## 3. Data sources

### Warcraft Logs API v2 (official: https://www.warcraftlogs.com/api/docs)
- The PoC uses only the **public** endpoint (`/api/v2/client`) with the client-credentials flow. The private endpoint (`/api/v2/user`, authorization-code flow) is for account linking and private reports and is out of scope here.
- Token: `POST https://www.warcraftlogs.com/oauth/token` with `grant_type=client_credentials`, HTTP Basic auth `client_id:client_secret`. Cache the token until expiry.
- API host for **Classic Era** is `WCL_API_HOST` (default `https://vanilla.warcraftlogs.com/api/v2/client`). If zone discovery returns no Naxxramas, try `https://classic.warcraftlogs.com/api/v2/client`. Never hardcode the host in code.
- **Discover IDs at runtime.** Do not hardcode zone or encounter IDs: run the zones query in `wcl-queries.graphql`, find the zone named "Naxxramas", store its encounters in `encounters`. Boss config in `boss-config.json` is keyed by boss *name*.
- **Resolve ability IDs by name** from each report's `masterData.abilities`. IDs listed in `boss-config.json` are hints only; names are authoritative.
- Use GraphQL introspection (the API supports it; browse with Altair or GraphiQL) whenever a field or argument in this brief doesn't match the live schema. The brief may be slightly off; the schema is right.
- **Rate limits:** a points-per-hour budget (commonly 3,600/hour per client; confirm via `rateLimitData`). Query it before large jobs; stop at 85% of `limitPerHour` and mark the job `paused` with a resume time. Every fetched object is cached, so re-runs cost nothing — caching is the documented way to stay within budget.
- **Report visibility:** the test report must be public or unlisted; private reports are not readable with client credentials.
- Only public reports. Attribute Warcraft Logs on every page that shows derived data.

### talentsforever.com
- `GET https://talentsforever.com/data.json` hourly at most, with `If-None-Match`. Store each new version in `source_snapshots` with the file's `generated` date and a checksum. This is the adapter pattern for all future game-data sources.

---

## 4. Pipeline (build in this order)

**Job A — Discover.** Fetch zones → find Naxxramas → upsert `encounters` for the three bosses (and store the rest; cheap).

**Job B — Rankings sample.** For each boss × spec: fetch `characterRankings` (metric `dps`, latest partition). Use the returned `count` to compute which pages correspond to the 76th, 85th, 94th percentile (band 75–94), the 95th and 97th (band 95–98), and page 1 (band 99+). Fetch those pages (100 parses each) and store rows in `ranked_parses` with a `band` label and the parse's `duration`. Start with **20 parses per band** (sample evenly from the fetched pages); make the per-band sample size a setting.

**Job C — Events for ranked parses.** For each sampled parse: fetch the report's fights + masterData (cached per report), then for the parse's `fightID` and the player's `sourceID`: `Casts`, `Buffs`, `DamageDone`, `Deaths`, and `CombatantInfo`. Paginate on `nextPageTimestamp`. Store raw pages in `raw_events`.

**Job D — Metrics.** Run the metric engine (`metrics-spec.md`) over each parse → `parse_metrics` (one row per parse, JSONB metric vector). Then build `reference_bands`: per boss × spec × kill-time bucket × band, the median and MAD of every metric, with `n`.

**Job E — Guild report ingest.** User pastes a report URL. Fetch fights + masterData + `rankings` (gives each player's `rankPercent` per fight); for each Naxx fight of the three bosses and each player of a supported spec, fetch the same event types and compute metrics. Kill-time bucket comes from the fight duration. Wipes are ingested too (for lethality), but reviews are generated for kills only.

**Job F — Review.** For a (report, fight, player): assemble the fact table → run attribution (`metrics-spec.md` §5) → render the technical block and the plain-language paragraph from templates → store in `reviews`. Deterministic: the same inputs must produce identical text.

**Job G — Lethality.** From `Deaths` events across all ingested fights of a boss: deaths per ability per pull, split tank vs non-tank (tank = a player who took ≥ 40% of boss melee damage in the fight), plus cascade detection (≥ 3 deaths within 5 s → attribute to the most recent boss cast before the first death).

**Job H — Talents snapshot poller.** Independent of A–G.

---

## 5. Metric engine

Implement exactly as specified in `metrics-spec.md`. Key points:
- Swing detection = Melee events + on-next-swing abilities, with same-timestamp extra attacks collapsed.
- Swing timer is **estimated empirically** from the parse's own inter-swing intervals (no item database needed in the PoC).
- Lost swings are computed per gap and classified: `forced_movement` (windows from `boss-config.json`), `cc` (debuff events on the player), `dead`, or `unexplained`.
- Every metric is a plain number with a unit, stored in one JSONB vector per parse, so bands and attribution are generic over metrics.

---

## 6. UI pages (minimal, functional)

1. `/setup` — API status (rate limit remaining), discovered encounters, buttons to run Jobs A–D and H with progress, sample-size setting.
2. `/bands` — table of reference bands per boss × spec × bucket: n, median, MAD per metric.
3. `/ingest` — paste a report URL → runs Job E → lists fights and players found.
4. `/review/[reportCode]/[fightId]/[playerName]` — the review: technical block, swing block, then the plain-language paragraph. A "show all metrics" expander.
5. `/boss/[name]` — lethality table and cascade list, plus the boss's abilities seen in logs (name, casts per pull, avg damage).

Every page that shows derived data includes "Data: Warcraft Logs" with a link to the source report(s).

---

## 7. Testing and fixtures

- Record real API responses once (one rankings page, one report's fights/masterData, one player's events for one Patchwerk fight, one Thaddius fight) into `tests/fixtures/*.json`. The metric engine, band builder, attribution, and template renderer must all run offline against these fixtures.
- Unit tests required: swing detection (counts match the report's Casts table for "Melee" ± the on-next-swing count), extra-attack collapsing, empirical swing-timer estimate within ±0.1 s of the known weapon speed for the fixture player, gap classification on the Thaddius fixture (Polarity Shift windows must be `forced_movement`), plain-paragraph linter (≤ 5 sentences, ≤ 1 number, no banned words), determinism (same input → same text).

---

## 8. Acceptance criteria (definition of done)

1. Job A discovers Naxxramas and the three bosses without hardcoded IDs.
2. Bands exist for both specs on all three bosses with n ≥ 20 per band, and `/bands` shows them.
3. Ingesting one public Naxx report produces reviews for at least three players across the three bosses.
4. Each review shows: parse percentile and band, strengths vs the band below, gap attribution to the next band (top 3 items with expected gain), the swing block with lost swings by cause, one ceiling line, and the plain paragraph that passes the linter.
5. `/boss/Thaddius` shows a lethality table with at least one cascade detected from an ingested wipe (use any public report containing wipes).
6. Re-running any job makes zero new API calls for already-cached objects.
7. All tests pass offline.

---

## 9. Conventions

- Every derived number is keyed by `patch` (store the report's game version string from the API) so future data doesn't mix.
- Comparisons are to bands, never to named players. No adjectives in review text. Templates live in `src/review/templates.ts`; the plain-paragraph rules live next to them and are enforced by the linter test.
- Log every API call (query name, points cost if returned, cache hit/miss) to a `api_calls` table; `/setup` shows the last 50.
- Keep functions pure where possible: `computeMetrics(events, config) -> vector`, `buildBands(vectors) -> bands`, `attribute(vector, bands) -> items`, `render(facts) -> text`.
