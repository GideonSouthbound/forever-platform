# Module F · Characters (talents, gear, sims)

**Purpose:** builds and gear sets per character, populated from logs, with a data foundation that outlives any single source. Tables: `source_snapshots`, `talent_builds`, `items`, `gear_sets`, `sim_results`.

**Note (25 Oct 2026):** Forever Logs' documented events carry no combatant info (gear and talents at the pull), which this spec assumed from Warcraft Logs. Until its armory is exposed (open question 3 in `13-forever-logs-api.md`), gear sets come from a character-export paste or manual entry, and the "signed vs logged" talent diff compares against the member's saved build. Phase 7.

## Talents
- Adapter for Talents Forever (CC BY 4.0, credit link required): hourly ETag poll → snapshot on change; builds reference their snapshot so old builds render after site rebuilds (the beta-client rebuild lands Sep 17). Fallback dataset: Deradon/wow-forever-talent-calc (MIT).
- Own tree component on the JSON: 51 points, rows unlock every 5 points per tree, prerequisite arrows, level = points + 9 (Legacy "Talented" perk), estimated ranks dimmed, "compare to Classic" from the `classic` block, icons via zamimg slugs.
- Share-link import: match Talents Forever's encoding once observed; members paste his links.
- Builds attached to characters (main/off-spec); officer-published raid builds per role; diff against the talent split WCL records at pull ("signed Prot, logged 31/20/0"); roster-wide "who's running what".

## Items and gear
- `items` from the multi-source adapter (03-integrations). Shared by Loot, gear audits, and the planner.
- Gear sets populate from WCL combatant info (item IDs at pull); members edit for what-ifs. Stat totals and resist sets require the item DB; until then, show item lists only.
- Gear/enchant/consume audit from last week's log flags missing enchants and empty slots before raid.

## Sim layers (later)
- Layer A ceiling: the WoWSims Forever fork (`github.com/ElliotWood/Forever`, classes converted incrementally; see 03-integrations `sim`) as WASM in the worker; a stat-weight (EP) model only for classes the fork hasn't converted. Hand-authored talent→stat effect table for the 10–20 stat-affecting talents per class.
- Layer B execution ratio: Module C actual ÷ Layer A ceiling on the same boss/bucket.
- Layer C team viability: Module D consumes Σ(ceiling × execution) vs requirement; healer throughput vs damage-intake curve; tank survivability.

## Acceptance
- Talent snapshot updates land within an hour of a change; three prior snapshots remain renderable.
- A character's gear set appears automatically after a report ingest.
- Ceiling values exist for every raider (engine or EP) and feed placement.
