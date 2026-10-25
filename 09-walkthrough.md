# 09 · How it all fits together — one raid week with sample characters

This is the integration spec in story form. The builder should be able to trace every step to a module, a table, and a job. Names are invented; numbers reuse the sample parse review from `poc/review-example.md`.

**Updated 25 Oct 2026.** Logs come from Forever Logs (`13-forever-logs-api.md`): close-out starts from a pasted report link, and every step that reads per-player log data needs the `events:read` scope. **The Dec 9 MVP covers Day 0 through Thursday's loot sheet, plus Friday's close-out without logs** (signups, voice presence, the Gargul paste); log ingest, reviews and lethality arrive in Phases 4–5, placement in Phase 6. Numbers in this story are illustrative: the CI test asserts `test-data/expected/walkthrough-expectations.json`, built from the TEST fixtures (Classic Era zones as placeholders).

## Cast

| Name | Class / role | Team | Notes |
|---|---|---|---|
| **Dunmar** | Prot Warrior, main tank | Vanguard (40) | Raid lead, `team:lead`, `org:admin` |
| **Maelis** | Holy Priest | Vanguard | Officer, loot master, `loot:manage` |
| **Thorvik** | Fury Warrior | Vanguard | Raider, review opt-in, 68th percentile on Onyxia |
| **Kessa** | Combat Rogue | Vanguard | 96th percentile; her logs feed the reference pool context checks |
| **Orla** | Resto Druid main / Mage alt | Vanguard main, Hearth alt | Multi-team member |
| **Pip** | Mage | applicant → Hearth | Thorvik's brother-in-law, new to raiding, `must_with` Thorvik on family nights |
| **Brann** | Hunter | Hearth (10) | Family, dies to whelps, low reliability score (officer-only) |

Teams: **Vanguard** (40-man progression, Onyxia's Lair), **Ember** (20-man, Hyjal Summit), **Hearth** (10-man family/casual, Barrow Deeps). One Discord server, one login.

---

## Day 0 · Seeding (Modules J, H, I)

1. Maelis uploads the guild's existing roster spreadsheet (`/imports`). Column mapping auto-detects Name/Class/Spec/Role/Team/Discord. Preview shows 47 creates, 0 errors. Apply → 47 `characters` with `status='pending'`, 47 `team_memberships` pending, one `roster_imports` row, one audit entry, and an officer-channel summary.
2. Thorvik joins Discord. The onboarding DM matches his handle to the pending character "Thorvik" → auto-claim: `characters.status='active'`, `claimed_at`, `users.discord_id` linked; membership becomes active; `team:raider` role synced. He answers "who do you play with?" → nothing yet. He opts into reviews.
3. Pip joins Discord with no pending character. The DM offers the pick-list, finds nothing, and routes him to the application (Module G) instead.

**Reads:** `roster_imports`, `characters` (pending). **Writes:** `characters`, `team_memberships`, `users`, `onboarding_progress`, `audit_log`.

## Monday · Recruitment (Module G) and the social graph (Module D input)

1. Pip applies at `/teams/hearth`: Mage, available Sat/Sun, links his Forever Logs profile. The screen card in `applications.screen` shows the link and his answers for officers to read. (An automatic parse summary, such as "Frost Mage, median 41st percentile, 12 logged kills", would need `events:read` and a character-level endpoint that Forever Logs does not document.)
2. A Discord thread opens in Hearth's officer channel with the screen card. Orla (Hearth officer) marks `trial`. Role sync adds `team:trial`.
3. Thorvik edits his profile: "plays with Pip" → `social_edges (thorvik, pip, must_with)`. This edge is now a hard constraint for the placement solver on any raid both could attend.

## Tuesday · One click creates Thursday (Module A W1, plus B, E, H)

Dunmar runs `/raid create team:vanguard zone:"Onyxia's Lair" when:"Thu 20:00" template:"Ony 40"`.

Pipeline steps (each recorded, each retryable):
1. `raid_events` row, status `planned`, seats copied from `raid_templates` including two **special seats** from `boss_guides.special_seats`: "whelp tank" (criticality high) and "add kiter" (high).
2. Raid-Helper event created in `#vanguard-signups` → `raid_helper_event_id`.
3. softres.it: `zones.softres_instance_id` is set for Onyxia → create → `softres_raid_id`, admin token encrypted. (If the instance ID were null, step 3 is skipped and `needs_attention: ['sr_link']` shows on the raid page with a paste field.)
4. Bot posts the public embed (Raid-Helper post + public SR link) and updates the week's SR-token summary message in the officer thread.
5. Status → `open`. Total elapsed: about six seconds.

Side effects: the ICS feed for every Vanguard member gains the event; the boss quick card for Onyxia (Module E) is linked from the embed; `#ui-updates` shows nothing new (the wago watcher found no Fojji Forever pack change this week).

## Wednesday · Signups, roster, attunement, and placement (Modules A W2 + W6, D, J)

1. The signup poller runs every 10 minutes: 43 accepted, 3 tentative, 2 bench. `signup_snapshots` grow; the roster builder shows role counts vs template: tanks 4/4, healers 9/10, DPS 30/26.
2. Overflow: four DPS must sit. **Bench fairness** reads benched counts from prior `raids.bench` and `social_edges`, so it never proposes benching half a friend group.
3. Dunmar opens the **placement tool** for the org's Thursday–Saturday plan. Inputs: `player_profiles` (execution ratio from Module C, reliability from deaths, attendance from credits, ceiling from Module F's stat-weight model), `team_capacity` (Vanguard on Onyxia: expected output 12% over requirement; Hearth on Barrow Deeps: 3% over), seats with criticality, social edges.
   - Solver output: Pip and Thorvik go to Hearth's Saturday Barrow Deeps run (must_with satisfied, both low-criticality DPS seats). Brann stays on Hearth but is moved off the "kite the pack" special seat (reliability 0.61 < 0.8 threshold) to a plain DPS seat. Hearth's margin after the change: 1%; the tool says "Hearth can absorb one more casual DPS, not two."
   - Dunmar applies the run → `placement_runs.applied=true`; Saturday's `seat_assignments` get `source='solver', status='pending'`; the bot DMs Pip and Brann signup links. Their Raid-Helper signups will confirm the seats automatically.
4. Lockout guard: Orla's alt is already saved to Ember's Wednesday Hyjal; the roster builder flags her alt as unavailable for Hearth's Saturday 10-man of the same lockout, so she's placed on her main for Vanguard only.
5. **Attunement guard** (A W6): the roster builder's attunement column shows two signed-up characters without the Drakefire Amulet. One is waiting on the General Drakkisath group step and appears on the officers' stuck list under Upper Blackrock Spire; the other has just started the chain. When Dunmar tries to move the second into an open DPS seat, the builder refuses: "Not attuned: Drakefire Amulet, current step: Questline started." Both stay benched for Onyxia; Maelis posts the stuck list to the officer channel, and an officer sets up a UBRS run for Saturday.

Members see: "You're on Hearth Saturday." Officers see: carry loads, margins, reliability. Nothing else crosses that line.

## Thursday T-2h · Loot sheet (Modules B, F, C)

1. Job `loot.sheet`: imports soft reserves from softres.it → `soft_reserves` (38 rows). Thorvik reserved the two-hander from Onyxia's table.
2. **SR sanity check** (needs gear data; not in the MVP): Module F's `gear_sets` show Thorvik does not have it → fine. Kessa reserved a dagger she already wears → flagged for Maelis. Forever Logs' documented events carry no gear, so `gear_sets` come from its armory if that is exposed (open question 3 in `13-forever-logs-api.md`) or from a character-export paste.
3. Engine (`sr_roll` method with attendance tie-breaks): for each item, ordered candidates with reasons. Thorvik on the two-hander: "SR; attendance 91%; no loot in 4 lockouts; wishlist rank 1." A second warrior with the same SR: "SR; attendance 78%; received tier piece 1 lockout ago." Thorvik lists first.
4. Output: `loot_sheets` row, `.xlsx` to R2, web table, officer-channel post. `loot_forecasts` updates: the two-hander has 3 contenders and an observed 0.4 drops/week → ~8 weeks to satisfy; the recruitment page's "open roles" line does not add a warrior this week.

## Thursday 20:00 · Raid night (Modules A W4, E, C)

1. **Control room** (Dunmar's tablet): voice presence vs signups — 41 present, Thorvik joined at 20:07 → `raids.late` (reliability nudge DM template, no public callout). Missing consumes from last week's logs (Phase 4+, and only if buffs present at the pull show up in Forever Logs' buff events): three players without a flask. Integration status: all green.
2. **Pre-pull briefing** for Onyxia, generated from `boss_abilities` lethality and `special_seats`: "Onyxia. Top three: Deep Breath, Bellowing Roar fear into Flame Breath, whelp waves. Special seats: whelp tank Dunmar, add kiter Kessa. Positions: ranged 30 yards on the flanks, melee behind the tail is death. Go."
3. Pull 3 wipes at 31% to a fear cascade in Phase 3. Dunmar updates the fear-spread note on the strat page's Phase 3 keyframe between pulls (`strats.version` 4 → 5; the reminder export regenerates in the background). The Forever Logs API serves processed reports only, so the autopsy arrives after upload: "Wipe at 31%: cascade began with Bellowing Roar at 4:02, 7 deaths in 5 s, 4 to Flame Breath while feared."
4. Pull 4 kills it in 3:52.

## Friday · Close-out (Modules A W5, B, C)

1. Maelis pastes the Forever Logs report link; `logs.ingest` fetches the report, its encounters, actors and events → `reports`, `raw_events` for all 40 players, archived to R2 on first read because retention is rolling. (At MVP, before logs, attendees come from signups and voice presence instead.) Attendees → `attendance_credits` (+1 Onyxia, weekly cap applied); Thorvik's late mark stays; signups-vs-attendees shows 2 no-shows and 1 walk-on.
2. Maelis pastes the Gargul award export → `loot_awards` (append-only). The two-hander dropped; Thorvik won it → his wishlist row gets `received_at`; the recency penalty will count against him next week; `loot_forecasts` recompute (2 contenders left).
3. If gear is available (Forever Logs armory, or members' character-export pastes), Thorvik's `gear_sets` row now includes the two-hander; the Module C swing timer for next week is estimated empirically from his swings either way.
4. Post-raid summary embed: 1 kill, 3 wipes, clear-time trend, top parses (Kessa 96), loot list.

## Saturday · Reviews (Module C)

Job `reviews.generate` runs for opt-in players on last week's kills.

For Thorvik on Onyxia (kill 3:52, bucket 3:30–5:30): fact table → bands (Fury Warrior, Onyxia, bucket, patch `forever-1.0`, n = 47) → attribution to the 75–94 band → templates. The technical block matches `poc/review-example.md`: 68th percentile, strengths (Rend uptime 84%, Death Wish 1 use), gap 11 points attributed to swing efficiency 46% (86% vs 94%), consumes 31%, Heroic Strike queue 14%, Sunder timing 9%; swing block: 118 of 137, 19 lost, all unexplained, 4 parries; ceiling line; trend. Then the plain paragraph: one in seven swings lost, get back on her after the whelp waves, stay behind her, bring Juju Power and Firewater.

- Delivered by DM with a link; `review_focus_history` records this week's focus (swing gaps after whelps, consumes). Next week's review will report whether it moved.
- Maelis (who can see reviews only if Thorvik shared his) sees nothing individual. Her officer view shows the **coaching queue**, which is empty this week: no opt-in player has had a stalled focus item for three weeks.
- Kessa's 96th-percentile kill enters the reference pool for Combat Rogue; the **context score** marks it generalizable (kill time and raid composition match the guild's own) so it strengthens next week's bands rather than being annotated as an outlier.

## Sunday · Standards, lethality, placement refresh, digest (Modules C, E, D, A)

1. `logs.stats.sync` refreshes the `/statistics` tables for Onyxia per spec; `bands.build` and `standards.build` rebuild with versions from the guild's own reports (other guilds' public reports only if Forever Logs agrees); the Fury Warrior Onyxia standard now says "Death Wish twice on kills over 3:30" for that bucket.
2. `lethality.build` updates `boss_abilities`: Bellowing Roar climbs to lethality rank 1 for Vanguard's own pulls; the boss page's "what actually kills us" reflects it; the pre-pull briefing text changes accordingly.
3. `player_profiles` recompute: Thorvik's execution ratio ticks up (new weapon raises his ceiling more than his actual, so the ratio dips slightly; the placement tool notes his seat is low-criticality anyway). Brann's reliability stays 0.61; Hearth's `team_capacity` recalculates after Saturday's kill (they cleared Barrow Deeps with Pip; margin 2%).
4. The **digest** posts to each team: upcoming raids, gaps ("Vanguard needs 1 healer Thursday"), loot awarded, parses (Kessa 96, Thorvik +9 points over three weeks, opt-in leaderboard by improvement), attendance changes. The recruitment page's open-roles line now reads "LF: 1 healer" for Vanguard.

---

## The data lineage in one table

| Step | Module | Reads | Writes |
|---|---|---|---|
| Roster import | J | sheet, `characters` | `roster_imports`, `characters(pending)`, `team_memberships(pending)` |
| Onboarding claim | H | `characters(pending)` | `users`, `characters(active)`, `onboarding_progress`, Discord roles |
| Application + screen | G | log profile link (a parse summary needs `events:read`) | `applications`, Discord thread |
| Social edge | D | — | `social_edges` |
| Raid create | A | `raid_templates`, `boss_guides.special_seats`, `zones` | `raid_events`, RH event, SR raid, embeds, `jobs` |
| Signups | A | Raid-Helper API | `signups`, `signup_snapshots` |
| Attunement | A | `attunements`, `character_attunements`, seats | readiness, stuck list, seat refusals, `audit_log` |
| Placement | D | `player_profiles`, `team_capacity`, seats, `social_edges`, `lockouts` | `placement_runs`, `seat_assignments(pending)`, DMs |
| Loot sheet | B, F | `soft_reserves`, `wishlists`, `attendance_credits`, `loot_awards`, `gear_sets` | `loot_sheets`, `loot_forecasts`, xlsx |
| Briefing / autopsy | E, C | `boss_abilities`, `strats`, live `reports` | briefing text, `cascades`, `strats(version+1)`, `reminder_exports` |
| Close-out | A, B, F | signups + voice (MVP) or Forever Logs report (Phase 4), Gargul export | `reports`, `raw_events`, `raids`, `attendance_credits`, `loot_awards`, `wishlists.received_at`, `gear_sets` |
| Reviews | C | `parse_metrics`, `reference_bands`, `review_focus_history` | `reviews`, `review_focus_history`, DMs |
| Weekly rebuilds | C, E, D | `/statistics`, own reports | `ranked_parses`, `reference_bands`, `rotation_standards`, `boss_abilities`, `player_profiles`, `team_capacity` |
| Digest | A, G | all of the above | Discord posts, recruitment page |

## Who sees what

| Persona | Sees | Never sees |
|---|---|---|
| Thorvik (raider) | his assignments, his reviews, his loot history, boss guides, team pages, his gear/talent builds | anyone else's review, carry loads, reliability, tiers |
| Pip (trial) | the same, plus his trial checklist | scorecard votes |
| Maelis (officer) | loot sheet with reasons, awards ledger, coaching queue, trial scorecards, integration status | individual reviews unless shared |
| Dunmar (raid lead / org admin) | everything above, placement tool, capacity margins, cross-team dashboard, jobs and audit log | — |

## The three loops that make it a system, not a set of pages

1. **Logs → gear → loot.** Gear sets sanity-check reserves; awards update wishlists and recency; the next sheet reflects it. With Warcraft Logs, combatant info filled the gear sets; Forever Logs' documented events carry no gear, so until its armory is exposed this loop runs on character-export pastes.
2. **Logs → reliability and execution → placement → seats → logs.** Deaths and execution ratios feed carry loads; the solver assigns seats with criticality from the boss guide; the raid's own logs update lethality, reliability, and capacity for next week.
3. **Logs → bands → reviews → focus → next week's review.** Reference pools rebuild weekly; each review commits to a small focus; the following review reports whether it moved. Improvement, not rank, is the thing the system rewards.

## Failure paths, same cast

- softres.it is down Tuesday: step 3 fails, `needs_attention: ['sr_link']`; Dunmar creates the sheet by hand later and pastes the link; the Thursday T-2h import proceeds normally.
- Vanguard's Thursday log was uploaded private: Forever Logs returns the same 404 for private and missing reports, so the close-out page says "report not found or not public; ask the uploader to make it public" and keeps the signups-and-voice attendance until a public link arrives.
- Raid-Helper's post arrives without buttons for a minute: the signup watcher waits for the edit before classifying (Temple hit this bug).
- The Forever Logs daily quota hits 85% mid-ingest: the job pauses with `resume_at` and continues the next day; reviews still generate from cached data and mark bands "provisional" where n < 30.
