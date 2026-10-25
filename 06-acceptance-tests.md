# 06 · Acceptance tests (cross-cutting)

Module-specific criteria live at the end of each `modules/*.md`. These apply to every phase. The Dec 1 MVP gate is listed below.

## Static / CI
- `grep` guard: no numeric zone/encounter/ability IDs in `packages/core` or `apps/*` outside `*.config.json` fixtures. Fails CI.
- Every table with derived data has `patch` and a test asserting it is set on insert.
- Every adapter has recorded fixtures and a `healthCheck()` test.
- Linter tests for every member-facing template (plain paragraph, briefing, DM nudges): sentence count, number count, banned words, no player names, no exclamation marks, determinism.

## Behavior
- Re-running any job with a warm cache makes zero external calls (assert on `api_calls`).
- Partial failure in the raid-create pipeline leaves a checklist with per-step retry; retry only redoes the failed step.
- Officer-only data (carry loads, tiers, reliability, others' reviews) is not reachable by a `team:raider` session (tRPC scope tests + Playwright).
- Member export contains every row referencing the member; delete removes them and keeps aggregates.
- Time zones: an event at 20:00 America/New_York renders correctly for Europe/London and Australia/Sydney viewers and in the ICS feed.

## Operations
- Backup exists for last night; restore drill passes in staging quarterly.
- Integration status board reflects a deliberately broken adapter within 15 minutes.
- Secrets rotation procedure in the runbook has been executed once end-to-end.

## MVP gate (Tue Dec 1)

Two parts, both required.

**1. CI, in TEST on fixtures only.** The walkthrough test runs this subset of the raid week and asserts the matching keys in `test-data/expected/walkthrough-expectations.json`. No combat logs are involved.

| Step | Asserts |
|---|---|
| Roster import, then the same file again | `roster_import`: 76 creates, 0 errors; re-import 0 creates, 0 duplicates |
| Onboarding | `onboarding.thorvik_fury`: auto-claim and opt-in recorded. Pip finds no pending character and gets the how-to-apply message (the application form is Module G, after the MVP) |
| Raid create, Thursday | `raid_create`: 5 recorded steps, SR step skipped in fixture mode, `needs_attention: sr_link`, cleared by pasting the fixture SR id |
| Raid-night roster import and signups sync | `signups`: 38 accepted / 2 tentative / 3 bench; pending seats confirmed by matching signups |
| Walls | `walls`: a character of the other faction and one on another ruleset are refused seats, each with a reason |
| Lockouts | `lockout_guard`: a character already saved to the zone that week is flagged |
| Attunement, on a Vanguard event from the `Ony 40` template | `attunement`: readiness 40/43; stuck list groups Ralvor under Upper Blackrock Spire and Ralwen under Blackrock Depths; Aelmir is refused a seat with a reason naming the Drakefire Amulet and his current step; Orla attuned, her alt Orlette not started; after one officer verify, Ralvor can be seated and readiness is 41/43 |
| Loot sheet, T-2h | `loot_sheet.Deathbringer`: Thorvik first, reasons include SR, attendance and no loot. The "already worn" flag reads gear from logs and joins the gate in Phase 4 |
| Close-out without logs | `close_out`: Thorvik late from voice presence; 4 awards from the Gargul paste; Thorvik's wishlist marks Deathbringer received |

Out of the MVP gate until their phase: log ingest and attendance from logs (Phase 4); reviews and lethality (Phase 5); placement (Phase 6); the digest and applications (when built).

**2. Humans, in the test Discord.** An officer other than the developer runs create raid → signups → SR paste → loot sheet → award paste end to end, and the result matches what the CI run asserts.

## Data quality (Module C, Phase 5)
- Swing detection: the count of `melee_only` damage events plus avoidance events matches an independent readout of the same encounter (Details!, or the raw `WoWCombatLog.txt`) within the on-next-swing count, on three fixture encounters. (The `poc/` version of this test compares against Warcraft Logs' Casts table on Era fights.)
- Forced movement: on the `poc/` fixture, Thaddius Polarity Shift windows classify as forced_movement and Patchwerk has zero forced-movement gaps. Re-point this test to the first Forever boss with a forced-movement mechanic once its logs exist.
- `is_glancing` and `is_crushing` nulls are treated as "not recorded", never as zero.
- Bands require n ≥ 30 (20 in poc) or mark fallback; the provisional label shows when n is below the threshold.
