# Module H · UI & Onboarding

**Purpose:** everyone runs the right addons and auras with zero hand-holding; new members get set up by a bot conversation. Tables: `ui_resources`, `wago_watch`, `onboarding_progress`.

## Required-UI page (per class)
Compatibility baseline: the Forever client reports itself as retail (`WOW_PROJECT_ID = 1`, beta build 1.60.1.69913) with Midnight's secret-values rules, so Midnight-built addons are the candidates and Classic-Era builds are not. Exclude private-server "Forever" (3.3.5a) addon listings from any watcher.
Only addons confirmed to run under Forever's Midnight-based API (see `11-dependency-status.md` and `12-in-game-ui-alternatives.md`). Primary for the whole frames/bars/nameplates/raid-frames/meter/bag/chat layer: **EllesmereUI, Forever build shipped (v9.6.7, 24 Oct 2026)**, with a **guild preset per role** (one-click import). Companions from the same author: **Standalone Cooldown Manager** and **Forever Essentials** (QoL; map markers, gathering tooltips, fishing). **Gargul `v8.0.1-forever`** for SoftRes import and loot rolls. **RaidHelper_Forever** (in-game addon) for encounter assignments and raid-buff checks — evaluate against Module A's roster tools before recommending it, to avoid two sources of truth. Otherwise, or alongside: a **Cooldown Manager layout per spec** (Blizzard built-in; shareable layouts, Cooldown Manager Profiles addon for import/export), boss mod (DBM confirmed building for Forever; BigWigs TBD), **Northern Sky Raid Tools** for reminders (if ported), Warcraft Logs uploader, Gargul (verify), Details!, Questie, OmniCD (officers), nameplates (Plater/Platynator, verify), bars/frames (Bartender4/ElvUI/Cell as confirmed). Fojji card: Discord invite + "guild subscription covers access" + status line "Fojji's packs are WeakAuras; WeakAuras does not run on Forever's API — watching for whatever he ships for Forever." Guild reminders arrive via Module E's reminder export, not a wago aura pack, until a WA-equivalent exists. Per-character "installed" checklist.

## Version watch
Hourly poller: wago public auras via the Companion's version-check endpoint; UI Pack pages by version/last-updated; **any Forever-labeled Fojji offering** (UI Pack, Plater/EllesmereUI profile, ElvUI profile, DBM/BigWigs profile — not only WeakAuras); DBM/BigWigs Forever release notes; **CurseForge's "WoW Forever 1.60.1" game-version filter** for EllesmereUI, NSRT, MRT, Plater, Gargul, Details!, Questie builds. Changes post to `#ui-updates` with changelog; `wago_watch.last_version` updates.

## Guild UI preset (replaces the parked wago pack)
EllesmereUI shipped for Forever (24 Oct 2026): publish guild presets per role (healer / tank-DPS) in its preset gallery or as import strings on the required-UI page; members import in one click; version them in `ui_resources` with a changelog line posted to `#ui-updates`. Boss reminders still ship through Module E's reminder export (NSRT/MRT/DBM), not through the UI preset. The wago aura pack idea stays parked unless a WeakAuras-equivalent appears. Never redistribute Fojji's Patreon-gated strings.

## Onboarding DM flow
Join Discord → bot DM: register characters (name/class/spec/main), pick team (or applicant), "who do you play with?" (social edges), review opt-in, timezone → roles assigned → welcome post → checklist link. ICS calendar feed per user.

## Acceptance
- A new member completes onboarding via DM in < 3 minutes and appears in the roster with roles.
- A version bump on a watched aura posts within an hour.
- Boss reminder edit → reminder export regenerates and versions automatically (target addon per beta findings).
