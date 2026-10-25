# test-data — mock data for the TEST environment

Everything the TEST environment needs to run the raid week in `09-walkthrough.md` with the sample cast, without touching the FOREVER configuration. TEST uses Classic Era zones and item names as placeholders (Forever raid loot tables are not announced). Regenerate with `python3 gen.py` (deterministic seed).

**The Dec 9 MVP (Phases 1–3) runs entirely on these fixtures; no combat logs are needed.** The steps and keys in the MVP gate are listed in `06-acceptance-tests.md`.

| File | Loads into | Notes |
|---|---|---|
| `seed.json` | org, teams, zones (Era), raid templates with seat criticality (incl. Vanguard `Ony 40`), boss guide special seats, social edges, test settings/flags | channel ids are `TEST_*` placeholders: replace with your test Discord server's ids. `logs_ingest` stays off until Phase 4 |
| `roster.xlsx` / `.csv` | Module J roster import → 76 pending characters + memberships | Vanguard 43 (40 + 3 bench), Ember 22, Hearth 11. Pip is deliberately absent |
| `raid-roster-vanguard-naxx-thu.xlsx` / `.csv` | Module J raid-night import → planned raid + 40 pending seats + 3 bench | special seats match `boss_guides.special_seats` by label |
| `wishlists.xlsx` / `.csv` | Module J wishlist import (315 rows, Era Naxx/Ony item names) | Thorvik rank 1 = Deathbringer |
| `availability.xlsx` / `.csv` | Module J availability import (77 rows incl. Pip) | Vanguard Tue–Thu, Hearth weekends, Pip Sat/Sun only |
| `applications.json` | Module G applications (Pip → Hearth; one healer → Vanguard) | after the MVP; includes the expected auto-screen card for Pip |
| `fixtures/discord.json` | discord adapter in `sandbox` mode: users, channels, onboarding answers, voice presence at raid start (Thorvik late 20:07) | |
| `fixtures/raid-helper.json` | raid-helper adapter in `fixture` mode: Thu Naxx + Ony event (38 accepted / 2 tentative / 3 bench), Sat Hearth event with Thorvik + Pip | |
| `fixtures/softres.json` | softres adapter in `fixture` mode: reserves for the Thu raid, incl. Kessa's flagged Kingsfall | |
| `fixtures/gargul-award-export.txt` | gargul adapter: 4 awards incl. Thorvik → Deathbringer | illustrative format; replace with a real export and keep the header row |
| `fixtures/attunements.json` | Module A W6: Drakefire Amulet rows per faction (illustrative Era step labels) + progress for Vanguard | 40/43 attuned; the three bench characters are mid-chain (Ralvor at Drakkisath, Ralwen at the Blackrock Depths step, Aelmir just started); Orla's alt Orlette has not started |
| `fixtures/wcl-reports.json` | **optional, `poc/` only**: public Era report codes + `log_name_map` | only needed to run the `poc/` metric math offline against Warcraft Logs |
| `expected/walkthrough-expectations.json` | golden checks for the CI walkthrough test | numeric review values are asserted only against the recorded poc fixture |

## Phase 4: combat-log fixtures
When Phase 4 starts (and `events:read` is granted), record the Forever Logs responses for one of the guild's own public raid reports (report, encounters, actors, events) into `fixtures/forever-logs/`, add a `log_name_map` that maps the five named test characters to real players of the same spec in that report, and set `logs_ingest` on in TEST. Re-record whenever the API's response shape moves (the events endpoints are marked experimental). Until then, the log-dependent expectations (`review_thorvik_onyxia`, `lethality`, the loot sheet's "already worn" flag) are out of the gate.

## Order of operations for the CI walkthrough test
**MVP subset:** seed → roster import (and re-import) → onboarding (discord fixture) → attunement fixture → raid create (RH + softres fixtures) → raid-night roster import → signups sync → walls and lockout checks → attunement gate on an `Ony 40` event → wishlist + availability imports → loot sheet → close-out without logs (voice presence, gargul awards) → assert the MVP keys in `expected/`.

**Full week, as phases land:** adds Pip's application (G), placement (Phase 6), log ingest and attendance from logs (Phase 4), reviews and lethality (Phase 5), and the digest.
