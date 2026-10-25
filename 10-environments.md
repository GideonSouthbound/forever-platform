# 10 · Environments: TEST (fixtures, Classic Era placeholders) vs FOREVER (production)

Same codebase, two configurations, two databases, two Discord servers. Nothing in TEST is ever copied into FOREVER except code and config shapes.

| | TEST | FOREVER |
|---|---|---|
| `APP_ENV` | `test` | `forever` |
| `GAME_PATCH` | `classic_era` | `forever-1.0` (bumped per content patch) |
| Database | `guild_test` (seeded from `test-data/seed.json`) | `guild_prod` |
| Discord | a private test server; bot in `sandbox` mode reads `fixtures/discord.json` for users/voice and posts to test channels | the real server; bot live |
| Raid-Helper | `fixture` mode (`fixtures/raid-helper.json`) or `sandbox` (real bot on the test server) | live API |
| softres.it | `fixture` mode; never creates real sheets | live behind `softres_auto_create` (off until Forever zones exist) |
| Combat logs (`logs` adapter) | MVP: off, no logs needed. Phase 4+: `fixture` mode with recorded Forever Logs responses from one of the guild's own reports, `log_name_map` applied. Warcraft Logs on Era reports only for the optional `poc/` math | Forever Logs `live`; `logs_ingest` on from Dec 9 once `events:read` is granted |
| Attunements | `fixtures/attunements.json` (illustrative Era step labels) | Onyxia row seeded from Blizzard's raid overview (20 Oct 2026); officers fill in the live quest steps |
| Talents Forever / wago pollers | on (they're real either way) | on |
| Item data | Era names seeded from wishlists; ids provisional | Forever source via the items adapter when one exists |
| Reviews | on, `band_min_n=20`, `sample_per_band=20` | on after first raids, `band_min_n=30`, provisional label under n |
| LLM rephrase | off | off (opt-in per org later) |

## Adapter modes
Every adapter exposes `mode: live | sandbox | fixture`. `fixture` reads the JSON in `test-data/fixtures/`; `sandbox` talks to real services pointed at test targets; `live` is production. Mode is config, never code. CI runs everything in `fixture` mode. Nothing in CI calls Forever Logs live: it needs a key, it is rate-limited, and its event endpoints are experimental, so the adapter is tested against recorded responses that are re-recorded when the shape moves.

## Name mapping in TEST (Phase 4+)
`settings.log_name_map` maps a test character to a real player in the recorded report (`fixtures/forever-logs/`, or `fixtures/wcl-reports.json` for the optional poc). Ingest applies it before character matching; it does not exist in FOREVER.

## Promotion
TEST → FOREVER promotes code and config shapes only: raid templates, boss-guide seat labels, loot configs, and strat layouts are re-created as `patch='forever-1.0'` rows by hand or migration. No characters, reviews, bands, or awards cross over. The `patch` column makes an accidental mix visible instantly.

## The CI walkthrough test
A single scripted integration test (`tests/walkthrough.test.ts`) runs the raid week from `09-walkthrough.md` end-to-end in TEST and asserts `test-data/expected/walkthrough-expectations.json`. It is the gate for every phase from Phase 1 on: a change that breaks any module's role in the week fails the build. Until Phase 4 it runs the MVP subset listed in `06-acceptance-tests.md`; log-dependent steps join as their phases land. Numeric review values are asserted against the recorded poc fixture; values from recorded Forever reports are asserted by shape and rule (band assignment, ≤ 3 focus items, linter).

## Cutover checklist (when Forever data exists)
1. Logging: **Forever Logs is the source** (`13-forever-logs-api.md`). Create a key, request the `events:read` scope for the guild project (post the key's `alog_` prefix in their Discord; never the full key), set the base URL, flip ingest on. If the scope is denied, follow the fallbacks in the roadmap's decision point. Re-check whether Warcraft Logs ever ships a Forever host; the `logs` adapter keeps both.
2. Forever zones on softres.it → fill `zones.softres_instance_id`, flip `softres_auto_create`.
3. Item source available (beta datamine is, as of Sep 17) → run the items adapter for `forever-1.0`; re-run at launch to confirm IDs.
4. First two raid weeks logged → bands build; reviews flip on when n ≥ 30 per band (provisional before).
5. Talents Forever rebuilt from the beta client — **done, `generated: 2026-10-23`, build 1.60.1.70425, with real spell IDs and a complete level-60 spellbook**. Verify the tree renders and regenerate the Forever metric config from this snapshot.
6. WoWSims Forever fork covers the guild's classes → enable Layer A per class; EP fallback for the rest.
7. Raids unlock Dec 9 → Phase 4 starts; bands go provisional until n ≥ 30.
