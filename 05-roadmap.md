# 05 · Roadmap and build order

**Version 2 (Oct 25, 2026). Replanned around raid unlock, not launch.** Launch needs no platform code because there is nothing to raid; raid night is where leadership's hours go. Dates assume one developer plus a builder agent, with leveling happening at the same time. Slip dates, not order. The Dec 1 gate is fixed.

## Calendar (Eastern time)

| Date | Event |
|---|---|
| Tue Oct 27, 4:00 p.m. | Early Name Reservation opens (NA 1:00 p.m. PDT), runs to Nov 3. Three characters total across all rulesets. |
| Wed Nov 4, 6:00 p.m. | Launch (3:00 p.m. PST; clocks fall back Nov 1). Everyone starts at level 1. |
| Nov 4 → Dec 9 | Five raid-free weeks: leveling, dungeons, the Drakefire Amulet chain for Onyxia. |
| **Tue Dec 1** | **MVP gate: a full raid-night run in the test Discord.** |
| **Wed Dec 9** | **Raids unlock** (time not announced): Barrow Deeps 10 / 8 bosses, Hyjal Summit 20 / 13 bosses, Onyxia's Lair 40. All three planned to reset weekly. |
| 2027 | Next tier on Blizzard's roadmap adds two raids. Zones and attunements are data rows, so this is a migration, not a rewrite. |

## This weekend: owner actions (no builder needed)

Before **Tue Oct 27, 4:00 p.m.**:
1. **Decided Oct 25: Horde on the RP-PvP ruleset, for every team** (one ruleset and faction means members can move between teams without hitting a wall). Announce and pin it in Discord with three notes:
   - **RP-PvP is confirmed for launch (Nov 4), but not yet for reservations.** Blizzard's Oct 22 blue post says they are "working hard" to make RP-PvP selectable when reservations open Tuesday. If it is not there, wait for their update rather than parking names on another ruleset: names are unique across the whole region, reservations are capped at three characters across all rulesets, and a character on the wrong ruleset cannot group with the team.
   - **RP naming rules apply on RP-PvP.** The full name has to be believable for a person in the world, with no joke or pun names (Method.gg guide, Oct 24). Blizzard force-renamed names during beta, and a forced rename loses the reserved name.
   - **One faction per account on PvP rulesets** (Method.gg), and RP-PvP mostly follows PvP rules, so every character reserved there should be Horde.
2. **Reserve your names.**
3. **Forever Logs access:** create an account and key in Profile Settings at https://foreverlogs.gg/profile (`stats:read` is self-serve), then join their Discord (https://foreverlogs.gg/discord) and post the key's visible `alog_` prefix plus a description of the project to request `events:read`. They upgrade the key in place. Record the answer in `11-dependency-status.md`, because it decides Module C's scope and the attendance source (see the decision point below).
4. **Discord setup:** per-team roles and channels (signups, officers, SR-token thread, ui-updates), the Raid-Helper bot with its API key, and a separate test server for the builder.

By **Nov 3** (reservation closes): collect a roster sheet of reserved names in the `test-data/roster.xlsx` column layout (first name, surname, class, spec, role, ruleset, faction, team, main/alt, Discord handle). That sheet is the Phase 1 import.

## Launch (Nov 4): build nothing

Discord roles, a pinned rules message (ruleset, faction, no GDKP, no gold buying), the Raid-Helper bot for leveling and dungeon groups, a team listing on forevercommunity.org, and members uploading dungeon logs to Forever Logs. Phase 1 runs in the background through launch; nothing on launch day depends on it.

## The December 9 MVP

| Phase | Window | Ships | Modules / key tables | Gate |
|---|---|---|---|---|
| **1 Core** | Oct 27 → Nov 10 | Tenancy; Discord login; teams with ruleset + faction; two-part character names; roster import from the reservation sheet, pending until claimed through the onboarding DM; role sync | I, J, H (onboarding only) · `orgs`, `users`, `teams`, `characters`, `team_memberships`, `roster_imports` | The real roster imports with zero duplicates, and a member claims their character in Discord |
| **2 Raid night** | Nov 10 → Nov 24 | One click: Raid-Helper event + Discord embeds + SR link (pasted until softres.it ships Forever); signups sync; roster builder that enforces ruleset/faction walls, exact seat counts and weekly lockouts; T-24h reminder | A (W1, W2) · `raid_templates`, `raid_events`, `signups`, `signup_snapshots`, `seat_assignments`, `lockouts` | One-click raid night in the test channel, and a Raid-Helper signup confirms a pending seat |
| **3 Attunement + loot** | Nov 17 → Dec 1 (overlaps 2) | **Attunement tracker:** Drakefire Amulet per character and faction, progress via `/attune`, officer verify, Onyxia readiness count, list of members stuck on a group step (Drakkisath in UBRS), unattuned characters blocked from Onyxia seats. **Loot:** SR import (softres.it export once live, paste until then), priority sheet with reasons from SR + attendance + recency, web table + officer post, Gargul award paste into the ledger | A (W6), B (minimal) · `attunements`, `character_attunements`, `soft_reserves`, `loot_configs`, `loot_sheets`, `loot_awards` | **Dec 1:** create raid → signups → SR → loot sheet → award paste, end to end in the test channel |
| **Dress rehearsal** | Dec 1 → Dec 8 | A mock raid night with real members in the real server; fix what breaks; write the officer runbook page | — | Officers run one raid night end to end without the developer |

**Attendance at MVP** comes from Raid-Helper signups, Discord voice presence at start time, and officer corrections. Attendance from logs arrives in Phase 4.

## After Dec 9 (in the order the logs allow)

| Phase | Window | Ships | Depends on |
|---|---|---|---|
| **4 Logs** | Dec 9 → Dec 31 | Forever Logs adapter; close-out from a pasted report id: attendance credits from each encounter's actor list, signups vs attendees, raw events archived on first read (retention is a rolling window) | Forever Logs key; `events:read` for reports and actors |
| **5 Coaching** | Jan 2027 | Module C reviews (swing efficiency, uptimes, cooldowns, consumes, deaths), lethality, wipe autopsy | Two raid weeks of logs; `events:read` |
| **6 Placement + guide** | Feb 2027 | Module D solver; Module E generated boss pages, JSON strats, reminder export (NSRT, MRT, RaidHelper_Forever, DBM) | Phase 5 player profiles |
| **7 Characters** | 2027 | Talent builds (the Talents Forever data, with spell IDs, is ready now), gear sets (Forever Logs armory if exposed, else a character-export paste), sim layers | WoWSims Forever class coverage |

## Decision point: the `events:read` answer

`/statistics` returns aggregate percentiles only. **Every per-player number (DPS, deaths, swings, attendance from a report) needs `events:read`**, so this one answer shapes Phases 4 and 5.

- **Granted:** attendance from encounter actors in Phase 4; the full metric engine in Phase 5. Per-metric reference bands built from other guilds' public reports **only if Forever Logs agrees** (asked in the request). Otherwise, bands come from the guild's own history, with outcome percentiles from `/statistics`.
- **Denied:** attendance stays on signups plus voice. Fallbacks for per-player data, in order: (1) ask again, scoped to the guild's own reports only; (2) parse the raw combat log ourselves, with members uploading the same `WoWCombatLog.txt` to the platform (a real build, but it removes the dependency for good); (3) a Details! export paste, placed against `/statistics` bands.

## If ahead of schedule (in this order)

1. Availability grid import and heatmap (J, A)
2. Leveling board: which spell rank each member should have at their level (Talents Forever spellbook levels), plus a character export paste
3. Wishlists (B)
4. Public team page and applications (G)
5. Required-UI page with the guild's EllesmereUI preset per role (H)

## Cut list if behind (cut from the top)

1. xlsx export (the web table and Discord post are enough)
2. The stuck-on-a-group-step list
3. T-24h reminder

**Never cut:** ruleset/faction walls in the roster builder, attunement gating for Onyxia seats, paste-a-link fallbacks for every external tool, the Dec 1 gate.

## The Classic Era proof of concept

**Reference only; no longer Phase 0.** It existed to prove the metric engine before Forever data existed, using the Warcraft Logs GraphQL API, which does not cover Forever. `poc/metrics-spec.md` and `08-review-templates.md` stay authoritative for Module C's metric math and review text; the WCL data layer and Era Naxx log fixtures are superseded by `13-forever-logs-api.md`. Build it only as an optional offline test of the math.

## Environment gate

Phases 1–3 run in the TEST environment entirely on fixtures (Discord, Raid-Helper, softres.it, Gargul, attunements); no combat logs are needed. The CI walkthrough gate covers the MVP steps listed in `06-acceptance-tests.md`. Log-dependent steps join the gate in Phase 4.

## Budget

The MVP is roughly a third of the full build. Whatever builder you use, set a hard spending cap per phase. If a phase blows through its cap without passing its gate, stop and fix the spec rather than pushing the agent.

## Weekly cadence

Mon plan · Tue–Thu build · Fri verify with the raid leads · weekends are for leveling. Each phase ends with a demo to officers.
