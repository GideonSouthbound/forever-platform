# Module A · Raid Ops

**Purpose:** one click from "we raid Thursday" to signups, soft-reserves, Discord posts, roster, attunement checks, reminders, and close-out. Tables: `raid_templates`, `raid_events`, `signups`, `signup_snapshots`, `availability`, `raids`, `attendance_credits`, `absences`, `lockouts`, `attunements`, `character_attunements`.

**In the Dec 9 MVP:** W1, W2 and W6 in full; W3 with the minimal loot sheet; W5 without logs. W4, the digest and the split-raid builder come after.

## Workflows
**W1 Create raid night** (`/raid create` or web) — inputs: team, zone, date/time, template.
1. Insert `raid_events` (planned). 2. Raid-Helper: create event → id. 3. softres (if flag on and `softres_instance_id` set) → ids/token (encrypted); else `needs_attention: ['sr_link']`. 4. Discord: public embed in signup channel (RH post + public SR link); admin link into the officer SR-token weekly summary message. 5. Status → open. Each step idempotent; failures land in a checklist on the raid page with a retry per step.

**W2 Availability & roster** — seats can be pre-assigned from a spreadsheet import (Module J) or the placement tool (Module D) as `seat_assignments` with status `pending`; a matching Raid-Helper signup confirms the seat automatically. Signup poller (5–10 min) → snapshots → roster builder: role/class counts vs template seats, tentative list, bench candidates (from bench-fairness counts), lockout conflicts flagged (a character saved to another 10-man that week). Recurring `availability` rows + signup history → availability heatmap and "best night to add a run" suggestion. T-24h reminder to non-responders (per-team setting: DM or channel).

**W3 Pre-raid** (T-2h) — SR import → loot sheet (Module B) → officer post; control-room view opens.

**W4 Raid night control room** (one page) — signups vs Discord voice presence, missing consumes (from last week's logs, Phase 4+), loot sheet, boss quick cards, integration status. Late/no-show detection: voice presence at start vs signups → `raids.late`, reliability, gentle DM template. `/wipe why` only if a live-logging source exists; the Forever Logs API serves fully processed reports only.

**W5 Close-out** — attendees → `attendance_credits` (per-zone weights, weekly cap, excused absences) → signups-vs-attendees comparison (signed & showed / benched / no-show / walk-on) → Gargul award paste → loot ledger → post-raid summary embed.
- **At MVP:** attendees come from Raid-Helper signups, Discord voice presence at start time, and officer corrections; the officer ticks the bosses killed.
- **From Phase 4:** an officer pastes the Forever Logs report link; attendees come from each encounter's actor list (needs `events:read`), and the summary adds wipes, clear-time trend and top parses. Pull within days, because event retention is a rolling window. Auto-attach needs a guild-scoped report listing, which Forever Logs does not document (open question in `13-forever-logs-api.md`).

**W6 Attunement tracker** (Phase 3, in the MVP) — tables `attunements`, `character_attunements`.
1. **Data.** One `attunements` row per zone × faction × patch with ordered steps (`key`, `label`, `group_step`, `location`, `final`). The FOREVER row for Onyxia's Lair is seeded from Blizzard's raid overview (20 Oct 2026): Drakefire Amulet, faction-specific questline, a final group step at General Drakkisath in Upper Blackrock Spire, the amulet carried in the bags. Officers fill in the intermediate quest steps from the live game in the admin UI; that is a data edit, not a deploy.
2. **Progress.** Members report with `/attune` (pick character, then step) or on their character page; officers set or verify any character from the roster view. `source`: `self`, `officer`, or `log` (from Phase 4, a character seen in an Onyxia's Lair encounter is attuned, because the raid requires the amulet). Every change writes `audit_log`.
3. **Views.** Team readiness per team and faction ("Onyxia's Lair: 31/40 attuned", counting characters, not users); per-character progress on the roster; a **stuck list** for officers of characters whose current step is a group step, grouped by location ("Upper Blackrock Spire: 6 waiting on Drakkisath"), with one click to post it to the officer channel; a readiness line in the Sunday digest.
4. **Gate.** The roster builder will not seat a character on an event whose zone has an attunement unless that character is attuned. The seat shows the reason ("Not attuned: Drakefire Amulet, current step: General Drakkisath"). There is no override: the fix is an officer verify, one click from the same screen.

**Digest** (Sunday) — upcoming raids, signup gaps ("need 2 healers Thu"), loot awarded, top parses, attendance changes; recruitment page updates from roster vs template.

## Rules
- Forever raids are fixed-size with fixed difficulty, and **all three reset weekly** (Blizzard, 20 Oct 2026): Barrow Deeps 10 / 8 bosses, Hyjal Summit 20 / 13 bosses, Onyxia's Lair 40. Templates carry exact seat counts.
- **Attunement is real and per character: Onyxia requires every raider to carry the Drakefire Amulet** (faction-specific questline ending at General Drakkisath in UBRS; in bags, need not be equipped). W6 tracks it per character, and the roster builder blocks unattuned characters from Onyxia seats. Fire resistance is called out by Blizzard for Onyxia, so the resist-gear check (Module B) is live for that raid.
- Attendance credits: per-zone weight (config), weekly cap, trailing-window eligibility thresholds per team; excused absences adjust automatically.
- Split-raid builder: from one 40-signup pool, propose balanced 10-man groups (roles, loot needs, friend groups from `social_edges`).
- ICS feed per user; timezone-aware everywhere.

## Acceptance
- One click produces RH event + Discord embed (+ SR when enabled) in < 10 s with per-step retry.
- Roster builder shows counts vs template, lockout conflicts, and bench candidates.
- Close-out computes credits and the signups-vs-attendees comparison from signups and voice presence (MVP), and from a pasted Forever Logs report (Phase 4).
- An unattuned character cannot be seated on an Onyxia's Lair event; the roster builder shows the reason, and one officer verify unblocks the seat.
- Attunement readiness is counted per team and faction, per character: a member's attuned main does not cover their alt.
- Adding a new attunement (the 2027 raids) is an `attunements` row with its steps, with no code change.
- Digest posts on schedule with correct gaps.
