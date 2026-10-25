# Module C · Performance (combat logs → coaching)

**Data source changed (24 Oct 2026):** the Forever logging site is **Forever Logs**, with a documented REST API — see `13-forever-logs-api.md`. Warcraft Logs has no Forever flavor. The metric engine in `poc/metrics-spec.md` still stands; what changes is that swings, avoidance outcomes and combat-start-relative timestamps arrive natively (`melee_only=true`, avoidance as its own event types, `timestamp_ms`), `damageMode=boss-only` replaces the hand-rolled padding filter, and `/statistics` supplies outcome-metric percentile bands directly. Per-metric bands (swing efficiency, uptimes, consumes, cooldown usage) still require the event stream and therefore the by-request `events:read` scope. Retention is a rolling window, so the guild's own events must be archived on first ingest.

**Without `events:read` this module has no input (25 Oct 2026).** `/statistics` gives bands but no per-player numbers, so even an outcome-percentile review needs the player's own number from the event stream. The fallbacks if the scope is denied are in the roadmap's decision point. Where this spec says fights, masterData, rankings or dataType (Warcraft Logs terms), read encounters, actors, `/statistics` and event groups; the mapping is in `13-forever-logs-api.md`. The documented events carry no combatant info, so the talent-conditional rules below read talents from the member's saved build (Module F) or infer them from casts and buffs. This module starts in Phase 5 (Jan 2027).

**Purpose:** turn logs into (1) opt-in individual reviews in a matter-of-fact tone, (2) log-derived rotation standards, (3) boss lethality and wipe autopsies. The `poc/` folder implements the core on Classic Era Naxx; this module generalizes it. Tables: `reports`, `raw_events`, `ranked_parses`, `parse_metrics`, `reference_bands`, `rotation_standards`, `outlier_annotations`, `reviews`, `review_focus_history`, `coaching_queue`, `boss_abilities`, `boss_deaths`, `cascades`.

## Ingest
Per report: fights, masterData, rankings (rankPercent per player per fight), then per player per fight: Casts, Buffs, Debuffs (on player), DamageDone, DamageTaken (tanks), Healing (healers), Deaths, CombatantInfo (gear, talents, auras at pull). Assignment tags (decurser, kiter, add duty) are attached from the raid's seat data so players are compared only within the same duty.

## Reference pool & context scoring
Weekly sample per boss × spec: `characterRankings` pages chosen to cover bands 75–94, 95–98, 99+ (page index from `count`). Each parse gets a **context score**: fight length vs boss median, healer count/mix, class stacking, world buffs and consume count, padding on adds, raid size. Parses outside the guild's own context are `generalizable=false` regardless of rank and are **annotated, not deleted**: `outlier_annotations.enabling_conditions` lists what made it work (e.g., no shield in combatant info, Defensive Stance uptime low, Death Wish cast outside the boss's dangerous window, tank overheal ≥ 40%, kill 40% faster than median). Kill-time buckets apply to everything.

## Forever rule differences (config, not code)
Expertise replaces weapon skill and racial weapon skills are gone, so dodge/parry avoidance checks read expertise from gear, not race; periodic damage can crit (dot uptime metrics gain a crit dimension); Improved Battle Shout is removed as a talent (drop it from uptime targets); Improved Slam (2 ranks) removes the swing interruption at 2/2 (clip detection is conditional on talents from combatant info); Flurry is 5%/rank (haste config ≈ 25% at 5/5); Weaponmaster's Sword line grants extra attacks, so extra-attack collapsing keys on the talent, not race; Death Wish adds +5% damage taken (outlier annotations read damage-taken, not armor); Precision is a hit talent (hit-cap checks read it); Alliance has Shaman, so Windfury extra-attack collapsing applies to both factions. See `11-dependency-status.md` for the dated source of each fact.

## Metric engine (see `poc/metrics-spec.md`)
Swing efficiency with gap classification (dead / cc / forced_movement / unexplained), empirical swing timer, clipping, parries as facing evidence, activity, uptimes, cooldown count/timing/phase alignment, consumes and buffs at pull, outcome. Healer set: throughput, overheal by target, assignment adherence, dispel latency. Tank set: damage-taken smoothing, cooldown coverage over dangerous windows, threat lead. Hunters: Auto Shot as the swing stream.

## Bands, attribution, reviews
Bands: median/MAD per metric per boss × spec × bucket × band, n ≥ 30 (poc: 20). Attribution to the **next band only**, ranked by expected gain × ease. Review = deterministic technical block (strengths vs band below, gap attribution, "this week" top 2–3, swing block, one ceiling line, trend) followed by a plain-language paragraph under linter rules (3–5 sentences, ≤ 1 number, one action, banned-word list, no names). Compare-to-yourself mode (this kill vs your best). Opt-in, weekly, DM + web; officers see nothing individual unless shared; officers can append one `coach_note`.

## Standards
From the generalizable pool: (state → action) priority lists, cooldown timing relative to pull and phase transitions (from the boss's own casts), uptime targets. Validate against a sim APL where one exists. Standards rebuild weekly and keep versions; early Forever weeks enforce minimum n and show "provisional".

## Boss lethality & autopsy
Deaths per ability per pull, tank vs raid, healer gap for tank deaths, cascades (≥ 3 deaths in 5 s → attribute to the last boss cast within 10 s). `/wipe why` on live reports: "wipe at 34%: cascade began with <ability> at 2:10, 6 deaths in 4 s, 3 to <ability> while feared."

## Retention-safe extras
Improvement leaderboard (opt-in, ranks percentile change), coaching queue (focus item unmoved 3 weeks → offer a class lead by execution ratio + availability overlap), consumable ROI shopping list with a bank-request button.

## Acceptance
- Poc acceptance criteria pass on Era; same code runs on Forever by config.
- Reviews render deterministically and pass the linter; opt-in and delivery work; trend and focus history update.
- Standards page shows a priority list and cooldown template per spec per boss with n and version.
- Lethality tables and at least one cascade from a wipe; `/wipe why` works on a live report.
