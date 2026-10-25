# Project handoff: WoW: Forever guild platform

**As of Sunday, Oct 25, 2026.** Start here if you are picking this project up in a new chat or as a new collaborator. The builder specs are the rest of this package; this file holds what lives outside them: the decisions and why, the current status, the to-do list, the working agreements, and where each idea from the brainstorm landed. A builder agent should start with `README.md` and `00-BUILD_BRIEF.md` instead.

---

## 1. The project in one page

- **What:** one web app plus one Discord bot for a community of 2–3 WoW: Forever guilds ("teams"). First, one-click raid nights (Raid-Helper event, soft-reserve link, Discord posts, roster with ruleset/faction walls and lockouts), attunement tracking, and a loot sheet. Later, coaching from combat logs, a placement tool for casuals, boss guides, and character tools.
- **Who:** Jason runs the community with his officers. The Replit Agent writes the code. Claude owns the specs and reviews each phase at its gate.
- **Community:** **Horde on the RP-PvP ruleset, every team** (decided Oct 25), so members can move between teams without hitting a wall.
- **Constraints:** no money anywhere (no treasury, no donations, no offering it to other guilds); learn from temple-era.com but design our own; built to run as long as Forever does; cheap and boring (about $30/month to host).

## 2. Key dates (Eastern)

| Date | What |
|---|---|
| Tue Oct 27, 4:00 p.m. | Early name reservation opens (1:00 p.m. PDT), runs to Nov 3. Three characters total across all rulesets |
| Wed Nov 4, 6:00 p.m. | Launch (3:00 p.m. PST). Everyone starts at level 1. No platform code needed |
| Tue Dec 1 | **MVP gate:** a full raid night end to end in the test Discord |
| Dec 1 → Dec 8 | Dress rehearsal with real members |
| Wed Dec 9 | **Raids unlock** (time not announced): Barrow Deeps 10, Hyjal Summit 20, Onyxia's Lair 40, all weekly resets |
| 2027 | Next tier adds two raids (a data migration, not a rewrite) |

## 3. Decisions, newest first

| Date | Decision | Why |
|---|---|---|
| Oct 25 | Horde, RP-PvP, every team | One ruleset and faction keeps members movable between teams |
| Oct 25 | Build around the **Dec 9 raid unlock**: MVP = core, one-click raid night, attunement tracker, loot sheet; gate fixed on Dec 1 | Launch has nothing to raid; raid night is where leadership's hours go |
| Oct 25 | Classic Era proof of concept is **reference only**, no longer Phase 0 | Its data layer was Warcraft Logs, which has no Forever flavor |
| Oct 24–25 | **Forever Logs** (foreverlogs.gg) is the combat-log source | Documented REST API; Warcraft Logs never added Forever |
| Oct 25 | `events:read` is the single dependency for per-player log data | `/statistics` is aggregate only; without the scope there are no reviews and no attendance from logs |
| Oct 20–24 | Attunement tracker is in the MVP | Onyxia requires the Drakefire Amulet on every raider, per character |
| Sep 18 | No WeakAuras; in-game reminders export to DBM / NSRT / MRT; EllesmereUI preset per role | Forever uses Midnight's addon rules, which WeakAuras does not run under |
| Sep 18 | Loot never models gold | Blizzard banned GDKP and is cracking down on gold buying |
| Sep 17 | TEST (fixtures, Classic Era placeholders) kept separate from FOREVER (production) | Build and test before Forever data exists |
| Sep 15 | No monetization of any kind; not offered as a service | Quality of life for our guilds only |
| Sep 15 | Package for a builder agent: adapters with manual fallbacks, no hardcoded game IDs, versioned game data, bands-never-people, officer-only analytics | Survive external tools changing or dying |

## 4. Status

- **Spec package:** v2.1, complete (this folder). Database layout verified to load in Postgres 16.
- **Forever Logs:** account and key created. **The first key was pasted into a chat, so delete it and create a new one before asking for the upgrade** (they upgrade the exact key you name). The request message is drafted (appendix of `13-forever-logs-api.md`) and not yet sent.
- **GitHub and Replit:** not started. Steps and the Phase 1 prompt are in `14-replit-workflow.md`.
- **Name reservation:** RP-PvP is confirmed for launch; whether it can be picked when reservations open Tuesday is not confirmed yet (Blizzard, Oct 22).

## 5. To-do, in order

1. **Before Tue 4:00 p.m.:** pin "Horde, RP-PvP" in Discord with the reservation notes (RP naming rules, one faction per account, wait if RP-PvP is not selectable yet; see `05-roadmap.md`). Pick names (appendix A).
2. **Forever Logs:** delete the exposed key, create a new one (https://foreverlogs.gg/profile), save it privately, and post the request with only the new key's visible `alog_` prefix in their Discord (https://foreverlogs.gg/discord). Record the answer in `11-dependency-status.md`.
3. **GitHub repo, then Replit import, then the Phase 1 run** (`14-replit-workflow.md`).
4. **Discord:** per-team roles and channels (signups, officers, SR-token thread, ui-updates), the Raid-Helper bot and its API key, a separate test server, and a Discord application (login credentials and bot token) whose secrets go into Replit Secrets.
5. **By Nov 3:** the roster sheet of reserved names, in the `test-data/roster.xlsx` column layout. It is the Phase 1 import.
6. Phases per `05-roadmap.md`: Dec 1 gate, Dec 1–8 rehearsal, Dec 9 raids.

## 6. Working agreements

- **The specs in the repo are the source of truth.** Changes flow: tell Claude → Claude updates the docs → upload to GitHub → sync in Replit → next agent run. If you ask Replit for a change directly, it records it in `docs/adr/`.
- **One phase per Replit run.** The agent stops at the gate, runs the tests, and lists every deviation from the spec.
- **Gate review:** bring "Phase N gate", the repo link (or a zip if the repo is private), and the agent's summary to Claude, who checks the code against the acceptance criteria and writes the fix list or the next prompt.
- **Secrets:** only in Replit Secrets. Never paste a full key into any chat. Forever Logs only ever needs the key's visible prefix.
- **Spending:** set a credit cap in Replit before the first run. If a phase blows its budget without passing its gate, fix the spec rather than pushing the agent. The earlier estimate (Sep 17; Replit pricing may have changed since) was $5k–9k over six months for the full build at Max settings; the MVP is roughly a third of the full build.

## 7. Where each brainstorm idea lives

| Idea | Where |
|---|---|
| One-click raids, signups, softres sheets, Discord posts, availability | Module A, `modules/A-raid-ops.md` |
| Loot priority, spreadsheet import and export | Modules B and J |
| Pending roster from an Excel sheet | Module J |
| Everything under one roof like temple-era: teams, recruitment, requirements, raid times | Modules G and I |
| Attunement tracking (Drakefire Amulet) | Module A, W6 |
| Opt-in parse reviews: matter-of-fact technical block, then a plain-language paragraph; small changes toward the next band; swing and auto-attack uptime | Module C, `08-review-templates.md`, `poc/metrics-spec.md`, `poc/review-example.md` |
| Rotations and cooldowns from strong parses, with top ~1% outliers annotated rather than copied | Module C (standards, outlier annotations) |
| Placement: where casuals, family and friends can go and every team still clears | Module D |
| Flip-through boss guide, lethality ("what kills us"), animated role tokens, special roles | Module E, `07-strat-format.json` |
| Talents Forever data (CC BY 4.0, credit link required) and a gear planner | Module F |
| Simulated fights with our own characters at their parse level | Module F (sim layers), later |
| Fojji: a link to his Discord until he ships something for Forever | Module H |
| Required UI: EllesmereUI preset per role, boss mods | Module H, `12-in-game-ui-alternatives.md` |
| Leveling board (which spell rank at which level) | `05-roadmap.md`, "if ahead of schedule" |
| Listing on forevercommunity.org | Module G |

## 8. Open questions and watch list

- Forever Logs: the `events:read` answer; the event retention window; whether comparison bands may use other guilds' public reports; whether the armory exposes gear (the event stream has no gear or talents).
- Blizzard: RP-PvP name reservation on Tuesday; raid unlock time on Dec 9; attunements for Barrow Deeps and Hyjal Summit (none announced); the Horde Drakefire Amulet quest steps in Forever (officers enter them as data).
- softres.it: Forever support ("Coming Soon"). Raid-Helper: Forever class templates.
- All of these are tracked in `11-dependency-status.md`.

---

## Appendix A: character names (for the reservation; not for the builder)

**RP-PvP naming rules** (Method.gg guide, Oct 24): the full name must be believable for a person in the game world, with no joke or pun names. Each part is 2–12 letters, with no numbers, apostrophes or hyphens and no letter three times in a row. Names are unique across the whole region on every ruleset. Blizzard forced renames during beta, and a forced rename loses the reserved name. "Southbound" reads like a Warcraft-style compound surname (compare Windrunner), so it will probably pass, but Blizzard makes the call.

**Likely to suit RP-PvP** (names that read as real people of a fantasy world):
- Medieval: Alaric, Leofric, Wulfric, Osric, Merrick, Anselm, Ranulf, Godfrey, Fulke, Bertram, Eustace, Cuthbert, Casimir, Lothar, Selwyn, Torrhen
- Germanic and Norse: Theodoric, Broderick, Garrick, Godric, Hakon, Ivar, Sigurd, Torvald, Rurik, Henrik, Alrik, Ulrik
- Celtic and place-names: Cormac, Maddock, Brannock, Havelock, Sedgwick, Fenwick, Renwick, Craddock, Murdock
- Roman: Maximilian, Praetorius, Ignatius, Hadrian, Tiberius, Magnus, Octavian, Valerian, Atticus, Cassius
- Old Testament and Puritan: Ezekiel, Obadiah, Malachi, Jedidiah, Zadok, Absalom, Gideon, Lazarus
- Short: Rook, Thane, Voss, Kade, Wren, Corin, Harlan, Locke, Brock

**Riskier on an RP ruleset:**
- Modern or joke registers: Chad, Jayquan, Comrade, Citizen, Sergeant, Cash, Dusty, Hank
- Borrowed famous characters: Tywin, Oberyn, Jorah, Drogo
- Household-name devils: Lucifer, Satan. Obscure grimoire names (Belial, Dantalion, Stolas) are less likely to be filtered, but whether they read as a believable person is Blizzard's call

**Earlier favorites:** Rook, Sawyer and Halloran Southbound; Ignatius, Bowie and Deacon; Alaric, Torrhen and Fulke; Belial, Dantalion and Absalom; Havelock, Cormac and Zadok. Of these, Bowie (a famous name) and Deacon (a title) are the ones to think twice about on RP-PvP. Your own: Maximilian and Praetorius Southbound fit; Jayquan, Chad and Comrade Southbound are the ones likely to be reported.
