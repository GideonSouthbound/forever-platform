# 03 · Integrations (adapter contracts)

Every adapter lives in `packages/integrations/<name>` and exports: a typed client, `healthCheck()`, a fixture-recording mode for tests, and a documented manual fallback. Config-driven hosts and IDs only.

## Discord (`discord`)
- **Identity:** Auth.js Discord provider on the web. Role sync nightly and on demand: team memberships ↔ Discord roles (config per team).
- **Bot (apps/bot):** slash commands `/raid create|roster|close`, `/sr <zone>`, `/loot sheet`, `/availability`, `/wipe why`, `/review me`; watches Raid-Helper signup posts in configured channels (note: Raid-Helper posts first, then edits buttons in; wait for the edit before classifying); posts embeds; maintains one editable SR-token summary per lockout week in the officer thread; reads voice channel presence at raid start for late detection.
- **Permissions needed:** Manage Roles, Send Messages, Embed Links, Create/Manage Threads, Read Message History, Message Content intent, View Voice States.
- **Fallback:** everything the bot posts can be copied from the web page.

## Raid-Helper (`raid-helper`)
- Server API key (from the bot's `/apikey`). Create events from templates in a team's signup channel; fetch an event with signups (status, class/spec, timestamps); event detail carries `softresId`.
- Poll open events every 5–10 min; store snapshots. Verify webhook availability before relying on it.
- **Fallback:** paste an event link; the app reads it.

## softres.it (`softres`) — no official API
- **Create:** reverse-engineered Inertia/Laravel POST: fetch homepage for session/CSRF → POST with the zone's `softres_instance_id` → read the 302 `Location` (raidId + adminToken). Resolve `Location` with `new URL(loc, base)`; never prepend blindly. Feature flag `softres_auto_create`.
- **Read reserves:** per-raid export (Gargul/CSV; community tools hit a JSON endpoint by raid id — confirm in DevTools). Import at T-2h and at raid start.
- Idempotency: one SR per (raid_event, zone). Backoff on errors. Admin tokens encrypted; never logged.
- **Forever:** softres.it lists "WoW: Forever — Coming Soon" in its edition selector as of 24 Oct 2026 but has not shipped it. Keep `softres_instance_id` nullable, the create flag off, and the paste-a-link fallback in place; re-check at launch.
- **Site rebuild (Sep 2026):** softres.it moved to a rebuilt site (legacy.softres.it retained) and added Raid Series with Bad Luck Protection. Re-verify the Inertia create flow and export endpoints against the new site before Phase 2; evaluate whether Raid Series/BLP should be imported into Module B for teams that run PUG-style loot.
- **Fallback:** "paste SR link" field on the raid page.

## Combat logs (`logs`) — Forever Logs primary, Warcraft Logs fallback
**As of 2026-10-24 the Forever logging site is Forever Logs (foreverlogs.gg), not Warcraft Logs.** It publishes a documented, versioned REST API with an OpenAPI 3.1 spec. The full contract, scopes, rate limits, event-stream semantics and footguns are in `13-forever-logs-api.md` — read that before writing the client. Key points for the adapter:
- Base `https://foreverlogs.gg/api/public/v1`, bearer key in a header (never the query string).
- `stats:read` self-serve; **`events:read` granted by hand to named projects** (post the key's `alog_` prefix in their Discord; never the full key). It gates every per-player number: without it there is no per-player data at all.
- `/statistics` returns percentile tables per class/spec with a `damageMode=boss-only` padding filter, which replaces most of the PoC's rankings sampling.
- Events: `melee_only=true`, avoidance outcomes as distinct event types, `timestamp_ms` from combat start, cursor paging up to 50,000 rows, cost per request not per row.
- `id` and `amount` are 64-bit **strings** — parse before arithmetic.
- Retention is a **rolling window**: archive the guild's own events on first ingest.
- Attribution link required wherever derived data is shown; no bulk redistribution; no competing log service.
- No upload API — officers paste a report id/URL; private reports 404 identically to missing ones, so guild logs must be public.
- No combatant info (gear, talents at the pull) in the documented event groups.
- Shared platform with 3.3.5 private-server log sites: some defaults are inherited (`difficulty` defaults to `ascended`), so pass every filter explicitly.

Both sites sit behind one `logs` interface so a Warcraft Logs Forever host, if it ever appears, is a config change.

## Warcraft Logs (`wcl`) — v2 GraphQL (official API, Classic Era / fallback)
Official docs: https://www.warcraftlogs.com/api/docs — this is the sanctioned way to read logs, and it is the backbone of Modules C, D, E, and F. Create a client at https://www.warcraftlogs.com/api/clients/.

- **Two endpoints, three auth flows.**
  - Public API `https://www.warcraftlogs.com/api/v2/client` with the **client-credentials** flow (token from `POST https://www.warcraftlogs.com/oauth/token`, `grant_type=client_credentials`, HTTP Basic `client_id:client_secret`). Public and unlisted reports, rankings, zones, game data. This is what the worker uses.
  - Private API `https://www.warcraftlogs.com/api/v2/user` with the **authorization-code** flow (`https://www.warcraftlogs.com/oauth/authorize` → `/oauth/token`). Needed to (a) link a member's WCL account and resolve their characters/guilds (`userData.currentUser`), and (b) read **private** reports. Store refresh tokens encrypted.
  - **PKCE** flow exists for browser-only apps; we don't need it because tokens are minted server-side.
- **Game flavors:** the docs describe the `www` host; Classic flavors are served on their own subdomains (Era: `vanilla.`; check which host returns Naxx Era data and which will serve Forever). `WCL_API_HOST` is config; the token endpoint is shared.
- **Schema:** GraphQL with full introspection; browse it with Altair/GraphiQL against the client endpoint. When this package's queries disagree with the live schema, the schema wins — log the deviation in an ADR.
- **Rate limits:** a points-per-hour budget (community clients report 3,600 points/hour per client; confirm via `rateLimitData { limitPerHour pointsSpentThisHour pointsResetIn }`). Query it before every large job, stop at 85%, resume automatically, cache every object; raw events archived to R2 after processing. Caching is the documented way to stay within budget.
- **Report visibility:** set guild logs to public or unlisted so the worker can read them with client credentials; private logs require the uploader to link their account. Put this in the raid-lead runbook.
- **Terms:** attribute Warcraft Logs on every page showing derived data with a link to the source report; don't replicate their site; respect the budget. Public-only sampling for reference pools.
- **Queries:** `poc/wcl-queries.graphql` (zones/encounters discovery, characterRankings, report fights + masterData + rankings, events with pagination, tables, guild reports for auto-attach, current user for account linking).
- **Live logging:** reports flagged `live` are re-polled every 60 s during raid windows for `/wipe why`.
- **Fallback:** paste a report link.

## Talents Forever (`talents-forever`)
- `GET https://talentsforever.com/data.json` (per-class files also exist). CC BY 4.0: credit with a link on every talent view.
- Hourly at most with `If-None-Match`; snapshot on change keyed by the file's `generated` date. The homepage can advertise a rebuild before the JSON export flips (observed Sep 17 evening: UI cites beta build 1.60.1.69876, JSON still `generated: 2026-09-13`); trust only the JSON field. Schema (as of Sep 13): `trees[] → talents[]` with 1-based `row`/`col`, `max`, `desc` (array when complete, rank-keyed object with `complete:false`/`confirmed[]` when estimated), `req` by name, `passive`, `cost`, `classic {status}`; plus `removed[]`, `spellbook`, `spell_desc`, `racials`, `legacy`. Expect the shape to change after the Sep 17 rebuild; parse defensively.
- Talent identity key: `(class, tree, row, col)` until spell IDs exist.
- Fallback dataset: `github.com/Deradon/wow-forever-talent-calc` (MIT; 469/470 talents; rank-1 text from footage, other ranks extrapolated and flagged per talent) — the same data the WoWSims Forever fork vendors. Use only if Talents Forever is unavailable; never merge the two silently.
- Icons: `https://wow.zamimg.com/images/wow/icons/large/<icon>.jpg`.

## wago.io (`wago`)
- Public auras: version-check endpoint used by the WeakAuras Companion (ids → version, changelog). UI Packs pages: scrape version + last-updated (respect robots; hourly max).
- Guild wago account hosts guild-authored content if a WA-equivalent exists for Forever; otherwise boss reminders ship through the Module E reminder export (DBM/BigWigs notes, raid-notes strings). Guild UI presets, if EllesmereUI ships for Forever, distribute through its preset gallery (ellesmereui.com) or import strings on the required-UI page.
- CurseForge game-version filter "WoW Forever 1.60.1": poll (respect robots; daily) for Forever builds of the addons in Module H.
- **EllesmereUI ships a Forever build** (v9.6.7, 24 Oct 2026), alongside a standalone Cooldown Manager and a Forever Essentials QoL addon; guild UI presets distribute through its preset gallery or import strings. Gargul ships `v8.0.1-forever` (3 Oct) for SoftRes import and loot rolls. `RaidHelper_Forever` (in-game addon, unrelated to the Discord bot) is a candidate reminder-export target.
- Fojji: Patreon-gated UI packs via Wago App; guild has a subscription. His packs are WeakAuras, which halted development for the Midnight API that Forever uses — watch for whatever he ships for Forever rather than assuming a WA pack. Never redistribute strings; link his Discord and FojjiCore.
- **Fallback:** manual "current version" field per resource.

## Item data (`items`) — multi-source
Adapter resolves to whichever source exists for the patch, in priority order: Blizzard Game Data API (if a Forever namespace ships) → wago.tools DB2 exports (Item/ItemSparse) → the WoWSims Forever fork's generated database (its scrapers read Wowhead's Forever database as of Sep 15, 2026) → beta-client datamine sites (daybreakforever.com/datamining lists items, set bonuses, talents new in the client) → WoWSims Forever fork data (`github.com/ElliotWood/Forever`) → That's My BIS item DB → manual CSV. Normalizes to the `items` table. Wowhead (wowhead.com/forever) is reference/tooltips only (terms). Beta-client IDs are expected to hold to live; re-verify at launch and keep `patch` on every row.

## WoWSims Forever engine (`sim`)
- `github.com/ElliotWood/Forever`: fork of wowsims/classic with a `forever` ruleset branch; classes are converted one at a time (Warlock, Priest, Druid, Shaman as of Sep 17). MythicSim hosts a Quick Sim on it; droptimizer planned once beta gear and loot tables exist.
- Adapter: build the engine to WASM in `apps/worker` (or call MythicSim's hosted sim if they publish an API); input = gear set + talent build + buffs; output = DPS/HPS ceiling with the engine version recorded. Classes not yet converted fall back to the EP model and are labeled.
- Treat results as directional until the community verifies talent values against beta; store `engine` and `settings` on every `sim_results` row.

## Character export addon (`export`, optional, Phase 1–3)
- Precedent: the WoW Forever Builds `/wfb` addon copies a one-line character string (class, race, level, spec, professions) for import on a website. A minimal guild addon (or adopting an existing export format) gives the platform level, spec, professions and equipped item IDs before Warcraft Logs data exists (Nov 4 – Dec 9). Members paste the string to the bot (`/import`) or the web; the parser validates and updates `characters`, a `professions` table and `gear_sets(source='addon')`. Combat state is never read, so it sits comfortably inside the addon policy.
- Fallback: the same fields typed into the onboarding DM.

## Gargul (in-game addon)
- Imports: softres.it "Gargul Export"; exports: loot awards after raid (paste → `loot_awards`). Consider a WeakAura or addon note export for boss reminders.

## Google Sheets (optional, `sheets`)
- Only if officers insist on editing loot sheets in a spreadsheet: push generated sheet, pull overrides. Default is `.xlsx` download + Discord post.

## Health board
`integration_status` updated every 15 min by pinging each adapter's `healthCheck()`; the raid-lead control room shows degraded integrations before raid time.
