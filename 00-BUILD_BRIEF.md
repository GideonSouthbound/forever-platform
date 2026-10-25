# WoW: Forever Guild Platform — Master Build Brief

**Version:** 2.0 (Oct 25, 2026) · supersedes 1.0 (Sep 15) · **Reference guild site:** temple-era.com (shape only; no code reuse)
**Key dates (Eastern):** name reservation opens Tue Oct 27, 4:00 p.m. (to Nov 3) · launch Wed Nov 4, 6:00 p.m. · **MVP gate Tue Dec 1** · **raids unlock Wed Dec 9** (Barrow Deeps 10, Hyjal Summit 20, Onyxia's Lair 40; weekly resets)
**Community:** Horde on the RP-PvP ruleset (decided Oct 25); every team shares that ruleset and faction.
**Money:** none. No donations, no billing, no paid tiers. This is a quality-of-life tool for one community of 2–3 guilds, built to run indefinitely.

---

## 1. What we're building

One web app + one Discord bot that removes the manual work from running raids for **2–3 in-game guilds ("teams") under one community**, and turns combat-log data from Forever Logs into coaching, placement, and boss knowledge that members actually use.

The product in one sentence: *a raid lead clicks once and everything downstream (signups, soft-reserves, Discord posts, attunement checks, loot sheet, log analysis, reviews) happens; a casual player gets a plain-language note on the one thing to do better; officers know which team can absorb whom and still clear.*

**First milestone, the Dec 9 MVP:** core, one-click raid night, the attunement tracker, and the loot sheet. Everything else follows the logs. Phases and gates are in `05-roadmap.md`.

**Modules** (each has a spec in `modules/`):

| # | Module | One line |
|---|---|---|
| A | Raid Ops | Create raid → Raid-Helper signup → SR link → Discord → roster builder (ruleset/faction walls, lockouts) → **attunement tracker** → reminders → close-out |
| B | Loot | SR import + generated priority sheet + Gargul awards ledger; wishlists and forecasting later |
| C | Performance | Forever Logs ingest → metrics → reference bands → opt-in parse reviews (technical + plain) → rotation standards → wipe autopsy |
| D | Placement | Carry budget per team, seat criticality, social graph, solver: "where can casuals go and still clear" |
| E | Boss Guide | Generated mechanics + lethality from logs, officer notes, animated strat pages, pre-pull briefing, in-game reminder export |
| F | Characters | Talents (Talents Forever adapter, spell IDs), item DB, log-populated gear sets, sim layers (later) |
| G | Recruitment & Retention | Public team pages, applications, listing on forevercommunity.org, trial scorecards, quiet-member flow |
| H | UI & Onboarding | Onboarding DM flow with character claims; required-UI page (EllesmereUI preset per role, Gargul, boss mod); version watch; ICS feeds |
| I | Multi-team & Platform | Tenancy, roles, guest pool, cross-team dashboards, jobs, integration status, backups, exports |
| J | Spreadsheet imports | Excel/CSV → pending rosters, raid-night rosters, wishlists, availability; claim-to-confirm; round-trip export |

**Read in this order:** `11-dependency-status.md` (current state of every external tool), `01-architecture.md`, `02-data-model.sql`, `03-integrations.md`, `13-forever-logs-api.md`, `09-walkthrough.md` (a raid week traced through every module), the module specs, then `05-roadmap.md`. The `poc/` folder is **reference only**: its metric spec and review templates are authoritative for Module C, but its Warcraft Logs data layer is superseded. Where an older spec says WCL or Warcraft Logs, read the `logs` adapter, which is Forever Logs in FOREVER.

---

## 2. Non-negotiable principles

1. **Adapters everywhere.** Raid-Helper, softres.it, Forever Logs (with a Warcraft Logs slot kept), Talents Forever, Gargul, wago, item-data sources: each sits behind an interface in `packages/integrations` with a manual fallback in the UI. When one changes or dies, one file changes.
2. **Discover, don't hardcode.** Zone, encounter, boss and ability IDs come from the APIs at runtime. Config is keyed by name or stable id (Forever Logs `boss_id`, Talents Forever spell ids) and by patch.
3. **Versioned game data.** Zones, attunements, items, talents, loot rules, credit weights, and reference bands are dated rows keyed by `patch`. A Forever content patch is a data migration, never a rewrite.
4. **Append-only where it matters.** Loot awards, attendance credits, reviews, and placement runs are ledgers; corrections are new rows.
5. **Bands, never people.** Every comparison a member sees is against a percentile band or their own history. No named comparisons anywhere in member-facing text.
6. **Officer-only analytics.** Carry loads, tiers, reliability scores, and individual reviews are never public. Members see assignments and their own reviews (opt-in).
7. **Deterministic text.** Review and briefing text comes from templates fed by a fact table. Same input → identical output. An LLM may rephrase only from the fact table with numbers locked, and only if explicitly enabled.
8. **Cheap and boring.** Postgres, Next.js, discord.js, pinned versions, under ~$30/month, no queues until they hurt.
9. **Own the data.** Nightly backups to object storage; one-click full JSON export per org and per member; raw combat events archived on first read, because Forever Logs retains events for a rolling window only.
10. **Bus factor ≥ 2.** Every account (domain, DNS, hosting, bot, Forever Logs key, wago) lives in an org account with two admins and a runbook in `docs/runbook.md`.

---

## 3. Stack and repo

```
apps/web            Next.js (App Router), TypeScript, tRPC, Drizzle, Auth.js (Discord), Tailwind
apps/bot            discord.js gateway: slash commands, signup-post watcher, embeds, threads, voice presence, role sync
apps/worker         long-running jobs: Forever Logs ingest and stats sync, talents/version pollers, nightly reports (can start inside apps/web via cron routes; split out when needed)
packages/db         Drizzle schema + migrations (02-data-model.sql is the reference)
packages/core       pure domain logic: lockout math, attunement rules, credits, loot engine, metric engine, bands, attribution, templates, placement solver, strat model
packages/integrations  raid-helper, softres, logs (forever-logs, wcl), talents-forever, gargul, wago, items (adapters + fixtures)
packages/contracts  zod schemas shared by web ↔ bot ↔ worker
docs/               runbook, ADRs, module specs (this package)
```

Hosting: Vercel (web + cron) · Railway or Fly (bot + worker, long-running) · Neon/Supabase Postgres · Cloudflare R2 for backups, exports and the raw-event archive · Sentry. Secrets via Doppler or the host's secret store. If developing on Replit: web + Postgres work natively; deploy the bot/worker as a Reserved VM or on Railway (they need a persistent process).

Testing: Vitest; every pure function in `packages/core` has fixture-based tests; every adapter has recorded-response fixtures; Playwright smoke tests for the five critical pages.

---

## 4. Phases (detail in `05-roadmap.md`)

| Phase | Window | Deliverable | Depends on |
|---|---|---|---|
| — | this weekend | Owner actions: ruleset + faction announced, names reserved, Forever Logs key + `events:read` request, Discord setup | nothing (owner) |
| 1 | Oct 27 → Nov 10 | Core: tenancy, Discord login, teams with ruleset + faction, roster import from the reservation sheet, onboarding claims, role sync | reservation roster sheet |
| 2 | Nov 10 → Nov 24 | Raid night: one-click Raid-Helper event + embeds + SR link, signups sync, roster builder with walls, seat counts and lockouts | Raid-Helper API key |
| 3 | Nov 17 → **Dec 1 gate** | Attunement tracker (Drakefire Amulet) + loot sheet (SR import, priority with reasons, Gargul award paste) | — |
| rehearsal | Dec 1 → Dec 8 | Mock raid night with real members; officer runbook | — |
| 4 | Dec 9 → Dec 31 | Forever Logs ingest, close-out with attendance credits, raw-event archive | `events:read` |
| 5 | Jan 2027 | Module C reviews, lethality, wipe autopsy | two raid weeks of logs; `events:read` |
| 6 | Feb 2027 | Placement (D), boss guide + reminder export (E) | Phase 5 profiles |
| 7 | 2027 | Characters: talent builds, gear sets, sim layers | WoWSims Forever coverage |

Launch day (Nov 4) needs no platform code. The `events:read` answer decides how much of Phases 4–5 is possible; the fallbacks are in the roadmap.

---

## 5. Definition of done per phase

Each module spec ends with acceptance criteria. Phase acceptance = all listed criteria for that phase's modules pass, plus: zero hardcoded IDs (grep-enforced), every derived number carries a `patch`, re-running any job makes no new API calls for cached objects, every member-facing text passes the linter, backups and exports run.

---

## 6. Dependency status (as of Oct 25, 2026; the dated log is `11-dependency-status.md`)

| Dependency | Status | Design response |
|---|---|---|
| Combat logs | **Forever Logs** (foreverlogs.gg): documented, versioned REST API. Warcraft Logs has no Forever flavor. The operator also runs private-server log sites, so some API defaults and FAQ text are inherited from those. Documented events carry no gear or talents at the pull | `logs` adapter, Forever Logs primary, WCL slot kept; request `events:read`; pass every filter explicitly and rely on no default (see `13-forever-logs-api.md`); gear sets from the armory if exposed, else a character-export paste |
| softres.it | "WoW: Forever — Coming Soon" in its edition picker | paste-a-link fallback; `softres_auto_create` off until it ships |
| Raid-Helper (Discord bot) | runs on Discord; no Forever class templates announced | build raid templates ourselves by raid size |
| Gargul | `v8.0.1-forever` shipped (Oct 3) | SR import, rolls, award export |
| EllesmereUI | Forever build shipped (v9.6.7, Oct 24), plus standalone Cooldown Manager and Forever Essentials | guild UI preset per role |
| Talents Forever | beta-client data with real spell ids and a complete level-60 spellbook (Oct 23) | adapter keys on spell ids; regenerate the Forever metric config from this snapshot |
| Attunements | Onyxia: Drakefire Amulet on every raider, per character; none announced for Barrow Deeps or Hyjal Summit | attunements are data rows; seed from Blizzard's raid overview (Oct 20) |
| Item database | beta datamine exists; raid loot tables unannounced | items adapter; Era item names stay in TEST fixtures as placeholders |
| Sim engine | WoWSims Forever fork, partial class coverage | Phase 7 |
| Blizzard API namespace | none | nothing depends on it |

---

## 7. Two environments

TEST runs the MVP (Phases 1–3) entirely on fixtures in `test-data/` (Discord, Raid-Helper, softres.it, Gargul, attunements); no combat logs are needed. From Phase 4, TEST adds Forever Logs public reports for adapter tests. FOREVER is production. See `10-environments.md`. The CI walkthrough test gates every phase; the MVP subset is listed in `06-acceptance-tests.md`.

## 8. How to work with this package

- Start with Phase 1. Build phases in order and stop at each gate for verification with real data. The Dec 1 gate is fixed.
- Treat every `.md` in `modules/` as the spec for one bounded context; do not merge contexts into one table or one service.
- When a spec conflicts with a live API, the live API wins; log the deviation in `docs/adr/`.
- Ask before adding a dependency, a queue, or a third-party service.
