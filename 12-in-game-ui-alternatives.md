# 12 · In-game UI alternatives to WeakAuras (research, Sep 17, 2026)

Forever runs Midnight's addon API (12.1.5), so the question is "what replaced WeakAuras in Midnight," then "which of those will exist for Forever." Everything below is Midnight-verified; Forever ports are unconfirmed until authors say so.

## What WeakAuras did, and what replaces each job

| WA job | Midnight replacement | Status | Notes for us |
|---|---|---|---|
| Personal cooldown/buff/proc tracking (class packs) | **Blizzard Cooldown Manager** (built-in): Essential cooldowns, Utility cooldowns, Tracked Bars (aura durations/pets), Tracked Buffs; alerts on cooldown-ready and pandemic; Midnight added shareable layouts. Community layouts on wago (e.g., Luxthos CDM imports); **Cooldown Manager Profiles** addon adds unlimited profiles, templates and full import/export | Working | The class-pack half of Fojji's WA packs maps here. Limits: no custom text, no non-ability resources, no conditional triggers |
| Party/raid cooldown visibility | **OmniCD** (combat-log based) | Working | Officer view for externals/interrupts |
| Boss timers and warnings | **DBM**, **BigWigs/LittleWigs**, plus Blizzard's built-in encounter timeline/warnings | Working; **DBM has announced a Forever build** | Encounter events remain available to boss mods |
| Per-boss phase reminders with text/TTS/glow | **Northern Sky Raid Tools (NSRT)** — per-boss reminders, cooldown assignments, CC on nameplates, shared via the addon's Shared Reminders; **WoWUtils/Viserio** plans and exports to it ("replacing the purpose of the Kaze WA and MRT Note") | Working, updated for Midnight restrictions | Primary target for Module E's reminder export if NSRT ports to Forever |
| Raid notes/assignments (plain text) | **Method Raid Tools** note (notes, reminders, assignments, ready checks) | Working; described as largely obsolete for retail raiding but still the simplest text channel | Universal fallback for the reminder export: plain text, no triggers |
| Nameplates with aura/cast highlights | **Plater**, **Platynator** (drag-and-drop designer, CC tracking), Blizzard nameplates with buff/debuff visibility | Working | Fojji may ship Plater/ElvUI profiles for Forever instead of WA |
| Raid frames with custom indicators | **Cell**, **ElvUI**, Blizzard raid frames | Working | |
| Meters | **Details!**, Blizzard's built-in meter | Working | Unaffected by combat-log restrictions |
| Rotation helpers, GTFO-style alerts, auto-marking, addon-to-addon combat comms | none | Removed by design | "Addons can display information; they can't compute decisions" |

## What this means for the guild
1. **Members' UI:** Cooldown Manager layout per spec (shareable), a boss mod, nameplates, meter. The required-UI page (Module H) lists exactly these once Forever versions exist, with import strings/profiles where the author allows.
2. **Boss reminders (Module E):** export adapter targets in priority order — NSRT reminder set (if ported), MRT note text (always), DBM/BigWigs custom bars, `/rw` macro text. WeakAuras stays a conditional target.
3. **Fojji:** his three UI packs are all WeakAuras (Classic, TBC, MoP; nothing for Midnight or Forever as of today). He has published ElvUI profiles before, so a Forever offering, if any, is likelier to be ElvUI/Plater/CDM profiles. The watcher looks for any Forever-labeled pack.
4. **Coaching moves out of game.** With in-combat "smart" auras gone, the plain-language parse reviews and the flip-through boss guide (Modules C and E) are the coaching channel. That was already the design; it is now the only option.


## EllesmereUI (checked Sep 18, 2026)

**What it is.** A free, modular all-in-one UI suite built natively for Midnight's API: created Mar 5, 2026 (Midnight launch), updated Sep 10, 2026, 5.4M lifetime downloads, on CurseForge, Wago and WoWUp. Twenty-plus modules in one addon: unit frames (player/target/focus/boss), action bars, healer-grade raid frames with debuff managers, nameplates with aura slots and interrupt-aware cast bars, a Cooldown Manager module (icons or bars), AuraBuff Reminders, resource and cast bars, damage meters, bags, chat, minimap, quest tracker, M+ timer, Blizzard skinning. "Unlock Mode" drag-and-drop editor with grid snapping; community presets import in one click; a preset gallery on ellesmereui.com. Its aura layer is a proprietary AuraKit written for the 12.1 aura APIs (the ElvUI team granted permission for its pixel-perfect logic). OakUI is a third-party installer of role-aware EllesmereUI profiles (v2.6.45, Sep 14, 2026) that can also inject DBM/BigWigs profiles.

**What it is not.** It is an ElvUI successor for the Midnight API, not a WeakAuras successor: no custom trigger/scripting system, no boss mod (the timer module is for Mythic+), no raid-note or phase-reminder feature. Its AuraBuff Reminders and Cooldown Manager modules are curated tracking within Blizzard's rules. Boss timers and per-phase reminders still come from DBM/BigWigs plus NSRT/MRT.

**Forever status, updated Oct 24, 2026: shipped.** EllesmereUI v9.6.7 has a Forever build, alongside a standalone Cooldown Manager and EllesmereUI Forever Essentials (beta, v9.6.1-forever, Oct 19). The guild preset per role is now a real deliverable for Module H. The history below is kept for the record.

**Forever status (Sep 18).** The developer's own X post says "EllesmereUI Forever is coming with beta next month" (pre-beta); CurseForge still lists retail only as of Sep 18. The repo states it targets "Midnight 12.1+ exclusively" with one codebase and no version gates, which is the right architecture for Forever since Forever shares the 12.1.5 API; a player on the Blizzard forums (Sep 15) reports the developer announced Forever support. Treat as **reported, unconfirmed** until a Forever build appears. CurseForge already lists "WoW Forever 1.60.1" as a game-version target, and the first dual-target addons (12.1.5 + 1.60.1) shipped on Sep 17, so authors can publish Forever builds now.

**How it fits the platform.** If it ships for Forever, it collapses most of the required-UI list into one addon plus a boss mod, and its one-click presets are the distribution mechanism the parked "guild wago pack" needed: the guild publishes an EllesmereUI preset per role (healer / tank-DPS) in the preset gallery or as an import string on the required-UI page, and members import it in one click. Boss reminders remain Module E's export to NSRT/MRT/DBM. Fojji's likeliest Forever offering, if any, would be an EllesmereUI or Plater preset rather than a WA pack.

**Caution:** search results for "Forever addons" include woweternity.com, a 3.3.5a private-server project that reuses the word Forever and lists "WeakAuras 2 verified"; it has nothing to do with Blizzard's WoW: Forever.

## Open questions to settle in beta
- Do NSRT, MRT, Plater/Platynator, OmniCD, Cell load on the Forever client (TOC/interface version), or do authors need a Forever build?
- Does the built-in Cooldown Manager exist in the Forever client, and does it support the Midnight sharing/import feature?
- Does DBM's Forever build expose custom-bar/note features usable by the reminder export?
- ~~Does Gargul (SR import, rolls) run unchanged?~~ A Forever build shipped Oct 3 (`v8.0.1-forever`).
- ~~Does EllesmereUI publish a Forever (1.60.1) build?~~ Yes, Oct 24 (v9.6.7). Still open: does OakUI or the preset gallery accept Forever presets?

## Sources
EllesmereUI: ellesmereui.com, GitHub EllesmereGaming/EllesmereUI, Addon Radar listing, OakUI on CurseForge, Blizzard forums "Addons that work" thread (Sep 15–17, 2026), Forever ClassicUI on CurseForge (Sep 17, 2026). Blizzard UI Discord statement and dev interviews via Icy Veins and the WoW Forever wiki; Blizzard Watch on the Cooldown Manager (Jan 16, 2026); WowCoach raid-tools roundup (Aug 18, 2026); Wowhead on Northern Sky Raid Tools; WoWUtils/Viserio prepatch update (Jan 20, 2026); ConquestCapped and BoostMatch Midnight addon guides (Jun 4 / Mar 5, 2026); Fojji's wago UI Packs profile; PCGamesN and Icy Veins on the WeakAuras team's decision.
