# 11 · External dependency status log

Dated snapshots of what exists outside our control. Newest first. The builder reads the top entry; older entries show what changed and when.

## 2026-10-25 — who runs Forever Logs, and what `events:read` decides

**Operator.** Forever Logs is run by The Dao of Logging, which also runs Triumvirate Logs, Frostmourne Logs and the archived Ascension Logs, all log sites for 3.3.5 private servers. Forever Logs is a tenant on that shared platform.

**It is Blizzard's game.** The 3.3.5 wording in parts of its FAQ raised the same name-collision worry as woweternity.com, so this was checked: its public reports include beta runs of Forever-only dungeons (Ruins of Lordaeron, The Hall of Thanes, City of Dalaran, Excavation Site: Wetlands). The 3.3.5 text is shared boilerplate from the sister sites.

**Inherited defaults.** `/statistics` takes `difficulty` = normal | heroic | mythic | ascended | all and defaults to `ascended`, an Ascension leftover. The client always passes `difficulty` explicitly and relies on no default; the `realm` filter's meaning for a realmless game is unverified. Details in `13-forever-logs-api.md`.

**Access process.** Create a key in Profile Settings (`stats:read` is self-serve), then post the key's visible `alog_` prefix and a sentence about the project in their Discord; they upgrade the key in place. Never share the full key, including with them.

**Correction to the Oct 24 reading: `/statistics` has no per-player numbers.** It supplies the bands, but placing a player in a band needs that player's own number, and only the event endpoints provide it. Without `events:read`, the API offers no per-player data at all: no DPS, deaths or swings per player, and no attendance from a report. That makes the `events:read` answer the single dependency for Phases 4–5. Fallbacks if denied (in order): ask again scoped to the guild's own reports; parse the raw `WoWCombatLog.txt` ourselves; accept a Details! export paste placed against `/statistics` bands. See the decision point in `05-roadmap.md`.

**Ruleset decision: Horde on RP-PvP.** Blizzard's Sep 21 post listed Normal, PvP, Roleplaying and Hardcore (Hardcore after launch). After player feedback, a blue post on Oct 22 added **Roleplay-PvP for launch on Nov 4** and said they are "working hard" to make it selectable for name reservation from Oct 27; not confirmed. RP-PvP mostly follows PvP rules (flagged outside sanctuaries and your own faction's territory), PvP rulesets allow one faction per account, and RP naming expectations apply: a believable in-world name, no joke names (Method.gg guide, Oct 24). Names are unique across the region on every ruleset. Data model: `rp_pvp` joins the ruleset vocabulary.

**Plan change.** The build is replanned around raid unlock (Dec 9), with a fixed MVP gate on Dec 1: core, one-click raid night, the attunement tracker, and the loot sheet. Launch day needs no platform code. The Classic Era proof of concept is reference material, no longer Phase 0.

| Dependency | Status (Oct 25) |
|---|---|
| Forever Logs `events:read` | **To request this weekend**; the answer decides Phases 4–5 |
| softres.it | "WoW: Forever — Coming Soon"; paste-a-link fallback stays |
| Raid-Helper (Discord bot) | no Forever templates announced; build templates by raid size |
| Gargul | `v8.0.1-forever` (Oct 3) |
| EllesmereUI | Forever build v9.6.7 (Oct 24) |
| Talents Forever | beta-client data with spell IDs (Oct 23) |
| Attunements | Onyxia: Drakefire Amulet per character; none announced for Barrow Deeps or Hyjal Summit |
| RP-PvP ruleset | added for launch (Oct 22); reservation support on Oct 27 not yet confirmed |

## 2026-10-24 — launch minus 11 days: the dependencies resolved

Beta closed 21 Oct (Blizzard's thank-you post, 23 Oct). **Early Name Reservation opens Tue 27 Oct, 1:00 p.m. PDT / 4:00 p.m. EDT**; launch 4 Nov, 3 p.m. PST; raids 9 Dec. Most of what was unknown in September now exists.

**Logging — solved, but not by Warcraft Logs.** WCL still has no Forever flavor. **Forever Logs (foreverlogs.gg)** is the de facto site and publishes a documented, versioned, read-only REST API with an OpenAPI 3.1 spec: `/statistics` (percentile tables per class/spec, with a `damageMode=boss-only` padding filter), `/phases`, `/bosses`, and event-level `/reports`, `/events`, `/actors`. Swings are `damage` + `spell_id: -1` with `melee_only=true`, and avoidance outcomes are their own event types — the swing-efficiency engine maps almost one-to-one. `stats:read` is self-serve; **`events:read` is granted by hand to named projects**, so request it now. Full contract, footguns and build consequences: `13-forever-logs-api.md`.

**Addons — shipped.** CurseForge and Wago now carry a Forever flavor (patch 1.60.1) and the pieces we need are live:
- **EllesmereUI v9.6.7 (24 Oct)** with a Forever build, plus **EllesmereUI Standalone Cooldown Manager** (same version/date) and **EllesmereUI Forever Essentials** (v9.6.1-forever, 19 Oct, beta, "many things added over the next month until official release"). Forever-specific work in its repo: map markers via a LoadOnDemand `EllesmereUIMapData` child addon, gathering skill in node tooltips, fishing. Its addon roster also wires a **Loot Council** group and a standalone `SimpleLootCouncil` — worth evaluating against Module B's council method.
- **Gargul v8.0.1-forever (3 Oct)**, "Supported Forever patch 1.60.1", on both CurseForge and Wago. SoftRes import and loot rolls are confirmed for Forever.
- **RaidHelper_Forever** (in-game addon, not the Discord bot; v1.0.1, 6 Oct): encounter assignments, auto-mark trash, raid-buff checks, attendance tracking, planned for Onyxia / Hyjal Summit / Barrow Deeps, with named roles (tanks, healers, interrupts, cube clickers, orb baiters, CC, beam soakers, weapon tanks). A candidate export target for Module E and an overlap to watch for Module A.
- Discord **Raid-Helper** (the bot) still has no Forever announcement; it needs Forever class/race templates, not a client build.

**softres.it** now lists **"WoW: Forever — Coming Soon"** in its edition selector. Not live; keep the flag off and the paste-a-link fallback in place.

**Talents Forever has fully flipped to beta-client data** (`generated: 2026-10-23`, build 1.60.1.70425). Every rank's text is real (`desc` is a full array, `complete: true`, `confirmed` lists every rank, `src: "beta"`), the spellbook is now level 60 complete with the level each rank is learned at, and **`spell_desc` entries carry real spell IDs** plus school, Classic-comparison fields and "not sold by the trainer" markers. Consequences: the talents adapter can key on spell IDs instead of names; the leveling board can tell a member which rank they should have at their level; and the Forever metric config should be regenerated from this snapshot, because several numbers moved since the demo-era reads (Shield Wall is now 60% for 12 sec on a 15 min cooldown, Deep Wounds 60%, Thunder Clap 20%/26 sec, Battle Shout 3 min, Slam gains a new rank 1 at level 20, Victory Rush heals 10%). Licence is explicitly CC BY 4.0, commercial use allowed with a credit link.

**Raids — official detail (Blizzard, 20 Oct).** Barrow Deeps 10-player, **8 bosses**, entrances via Mount Hyjal, Winterspring and Blackmaw Hold. Hyjal Summit 20-player, **13 bosses**, multiple paths. Onyxia's Lair 40-player, three phases, build fire resistance. **All three are planned to reset weekly.** And a correction to the September note: **Onyxia requires the Drakefire Amulet on every raider**, earned per character through a faction-specific questline ending at General Drakkisath in UBRS; it must be in the bags but does not need to be equipped. Attunement tracking is a real Phase 3 feature, not a placeholder.

**Name reservation mechanics** (Blizzard, 20 Oct): up to three characters **total across all rulesets**, first-come-first-served; creating two on PvP leaves only one for Normal or RP (that restriction applies only during the reservation window). Names are two-part and **the full combination** must be unique per region, so a shared first name is fine if the surname differs — a single family surname across all three characters works. Class and ruleset picked at reservation are what you level from 4 Nov; characters still start at level 1.

**New: a community recruitment channel.** forevercommunity.org is a community-run guild finder for Forever (guild pages with openings and schedules, player profiles, applications, a forum), Discord login. Worth listing the teams there and worth watching as prior art for Module G.

## 2026-09-18 — Blizzard's economy stance (policy, not tooling)

- **GDKP is banned in Forever.** Josh Greenfield (Senior Game Designer), WoW Forever Q&A stream, Sep 17: "The short answer is no, we are not going to allow GDKP." Reasons given: GDKP tends "to reach a level of ubiquity" that overtakes the guild structure; it is a "big barrier to entry for new players"; and "GDKP is an excellent way for bad actors to launder large sums of gold." A Blizzard forum representative ("Ebonhardt") is cited by players saying it "will be staying banned."
- **Gold buying enforcement:** Greenfield: "we do try, whenever we can, action accounts of buyers, or sellers, or bots" and "we try to haul that money back"; Blizzard will be "very, very actively monitoring the economy." Wowhead's recap paraphrases that Blizzard considers past enforcement on buyers too lenient and will crack down aggressively, implying permanent bans — paraphrase, not a quoted policy.
- **No WoW Token, no paid character boosts** — "no plans ... at least for now" (developer interviews, ~Sep 14). **Anti-boosting mechanics:** dungeon mob XP "brought way down," dungeon quest XP "much, much, much higher," so repeat dungeon runs are a poor leveling path.
- **Consequences for the platform:** loot methods are SR+roll, priority points, or council only; nothing in the platform ever models gold, and the loot config vocabulary excludes GDKP by construction. Team pages (Module G) can publish a "no GDKP, no gold buying" rule and onboarding can ask members to acknowledge it. The leveling board and dungeon LFG (Module A extras) should value first-run dungeon quests, not repeat farming.

## 2026-09-18 night — third sweep

- **Forever client identifies as retail.** A hands-on addon test against beta build 1.60.1.69913 reports `WOW_PROJECT_ID = 1` (retail), item/spell/talent calls moved to `C_` namespaces, unit health returned as secret values (third-party raid frames break), and secure snippets failing to compile (action-bar paging and click-casting broken — possibly beta breakage rather than policy). Practical rule: **Midnight-built addons are the compatibility baseline for Forever; Classic-Era addons are not.** Source is a third-party site's own testing, not Blizzard.
- **EllesmereUI:** the developer's own X post reads "EllesmereUI Forever is coming with beta next month" (pre-beta post; the tweet itself is not fetchable). CurseForge still lists retail 12.x only (v9.1.8, Sep 10). Status upgraded from "player report" to "developer-stated, not yet shipped."
- **Raid facts from devs (Ana Resendez, Clayton Stone, via recap):** the new raids launch at 10 and 20 players with no flex sizing and fixed difficulty; **no attunement required at launch**. Templates stay fixed-size; the pre-raid checklist drops attunements for Dec 9.
- **GDKP banned outright** (Blizzard statement via recap). No effect on us beyond confirming the loot module never models gold.
- **Beta launch day:** hour-plus queues and disconnects on Sep 17 (Blizzard: "scaling up"); addon reports are therefore thin for another day or two.
- **Name-collision warning for the watcher:** "woweternity.com" lists "Forever v1.2.0 (3.3.5a core)" addons including "WeakAuras 2 verified" — that is a private-server project reusing the word Forever, not Blizzard's WoW: Forever. Exclude that domain from any automated dependency polling.
- **Unchanged:** Talents Forever JSON still `generated: 2026-09-13`; no Warcraft Logs, softres.it, Raid-Helper or Blizzard-API Forever announcements.

## 2026-09-18 morning — second sweep (integration-relevant)

- **Realmless design changes the character model.** Blizzard's deep dive: players pick a ruleset (Normal, PvP, RP; Hardcore later) instead of a realm; dungeons and raids are same-ruleset only; no cross-faction grouping; character names are **two-part (first name + surname, e.g. "Ana Forever") and unique per region**, not per realm. Guild scope (per ruleset / per region) is unpublished. Consequences: `characters` needs `first_name`, `surname`, `ruleset`, `region`, `faction` (uniqueness = region + full name); teams carry `ruleset` and `faction` as hard constraints for placement and roster; softres/Raid-Helper name matching must normalize two-part names; Warcraft Logs character identity for Forever is unknown until their host appears.
- **Q&A stream (Sep 17), via a secondary recap:** third-party combat-log parsers reportedly validated for event sequencing and timestamps; basic UI addons, bags and unit frames functional in beta while automated combat scripting stays restricted; five-week gap to Dec 9 raids described as intentional; 10-signature guild charters. Treat the parser claim as encouraging but unverified until Warcraft Logs speaks.
- **Item/spell data pipeline exists in the open:** the WoWSims Forever fork added a `-wowhead=forever` mode to its database scrapers on Sep 15, pulling items and spells from Wowhead's Forever database. Our items adapter can consume the fork's generated database rather than scraping Wowhead ourselves.
- **Character export precedent:** the "WoW Forever Builds" site ships a `/wfb` addon that copies a one-line string (class, race, level, spec, professions) for import on their site; Forever build announced Sep 15, pending beta testing. Same pattern we can use: a tiny guild addon (or a shared export format) that members paste to the bot for the leveling board, professions directory and pre-raid gear sets during Nov 4 – Dec 9, before any Warcraft Logs data exists.
- **Talents Forever JSON still `generated: 2026-09-13`** (UI cites the beta build; export not yet flipped). Adapter unaffected.
- **Warcraft Logs, softres.it, Raid-Helper, Blizzard API:** no Forever announcements found.

## 2026-09-18 morning — first Forever addon signals

- **CurseForge has a "WoW Forever 1.60.1" game-version target**, and the first dual-target addons (12.1.5 + 1.60.1) shipped Sep 17. Authors can publish Forever builds now; the Module H watcher polls this filter for the addons we care about.
- **EllesmereUI** (free all-in-one UI suite built for Midnight's API; 5.4M downloads; ElvUI-class scope plus Cooldown Manager and aura reminder modules; one-click presets): a forum report (Sep 15) says the developer announced Forever support. Unconfirmed until a 1.60.1 build appears. If it lands, it becomes the primary UI recommendation and its presets replace the parked guild wago pack. It is not a WeakAuras or boss-mod replacement; NSRT/MRT/DBM still carry reminders and timers. Details in `12-in-game-ui-alternatives.md`.
- **Cooldown Manager in Forever:** forum hearsay that Blizzard will include it; unconfirmed.

## 2026-09-17 night — addon policy (affects Modules E and H)

- **Addons are allowed in Forever, under Midnight's API.** A Blizzard representative in the WoW UI Discord (Sep 16–17) confirmed addons "will be a part of the Forever experience" with "the same API restrictions introduced with Midnight" — Forever shares the vast majority of the 12.1.5 API. Lead designers Tim Jones and Mike Nuthals (BlizzCon/Kotaku) confirmed limits on "computational" addons: in-combat restrictions on automated marking/communication; the stated goal is that addons provide no objective competitive advantage.
- **What Midnight's "secret values" block:** addon access to personal combat state in combat — buffs, cooldowns, health, primary resources. Blizzard loosened some of it during Midnight beta (secondary resources, personal spell-cast tracking, color interpolation on unit frames) but not cooldown data.
- **WeakAuras, as a project, does not run on this API.** The WeakAuras team halted development for Midnight (Nov 2025) and said the loosened restrictions "don't pass muster"; a version with only non-combat triggers is "nearly useless." No reversal reported. Consequence: **no Forever WeakAuras unless the team reverses or a fork appears** — treat WA as unavailable for planning.
- **Boss mods:** DBM has announced it will build for Forever; BigWigs unconfirmed. Encounter warnings are expected to work within the restrictions (Midnight kept boss mods alive alongside Blizzard's built-in cooldown manager and encounter warnings).
- **Beta status:** nothing confirmed from the live client yet; addon-tracking sites mark every Classic addon "Forever support unconfirmed" except their own. Player report in the first week will settle: Details!, Questie, Bartender/ElvUI, Plater, DBM/BigWigs, Gargul, and whether `WoWCombatLog.txt` + Warcraft Logs uploads work (combat logging is a client feature separate from the addon API; it kept working in Midnight).

**Research on replacements:** `12-in-game-ui-alternatives.md` (Cooldown Manager, NSRT, MRT note, OmniCD, Plater/Platynator, Cell, DBM/BigWigs).

**Design consequences (applied to the package):**
- Module E's "WeakAura export" becomes a generic **in-game reminder export adapter** with targets chosen once the beta confirms what runs: DBM/BigWigs custom notes or timers, a raid-notes addon string, Blizzard's built-in encounter warnings, or a plain macro/text block. WeakAuras is listed only as a conditional target.
- Module H's Fojji card and the "Forever pack" watcher now watch for **whatever Fojji ships for Forever** (his packs are WeakAuras today); the guild wago pack is parked until a delivery mechanism exists. The required-UI page lists Midnight-API-compatible addons only.
- **Module C's value rises.** With fewer in-game combat helpers, post-raid log review is the main coaching channel; the plain-language reviews and boss guides do the job WeakAura reminders used to.
- Gargul depends on the addon API for SR import and loot rolls; confirm it runs (it is not a combat-state addon, so likely fine) before Phase 3.

## 2026-09-17 evening (beta live)

**Beta is open.** Level cap 20 for two weeks, then 30 to Oct 21; nothing raid-related is testable. What the beta *can* answer for this platform, in priority order: (1) does the client write `WoWCombatLog.txt` and does the Warcraft Logs uploader accept a Forever log — the single biggest dependency; (2) how realm/ruleset appear on a character (`characters.realm` semantics); (3) whether Raid-Helper's class/spec pickers need a Forever template (Skyborne, Dwarf Shaman, Human Hunter, Undead Paladin).

**Talents Forever is half-flipped.** The calculator UI now cites the beta client (build 1.60.1.69876) for talents, racials and Legacy perks, but the raw export (`data/*.json`) still says `generated: 2026-09-13` with demo-footage data and rank-keyed `desc` objects. The adapter keys on the JSON's `generated` field, never the homepage notice; expect the export to flip within a day, likely with full `desc` arrays and possibly a build field. Spellbook text stays demo-sourced until his beta pass.

**Talent facts that change Forever config (from the beta-client trees; config keyed `forever-1.0`, not code):**
- Flurry is 5% per rank (Classic 10%) → `haste_buffs.Flurry.haste_pct` ≈ 0.25 at 5/5, not 0.30.
- Weaponmaster replaces the weapon specializations; its Sword line grants a 1%/rank extra attack → extra-attack collapsing keys on the talent (from combatant info), not on race.
- Death Wish now adds +5% damage taken instead of −20% armor/resist → the "reckless tank" outlier annotation reads damage-taken deltas, not armor.
- Improved Slam has 2 ranks and removes the swing interruption at 2/2 → clip detection is conditional on talents.
- Improved Battle Shout and Improved Demoralizing Shout are removed as talents → drop from Fury uptime targets.
- Precision (+1% hit/rank) and Boundless Rage (+10 max rage/rank) are new Fury talents; Vitality and Bastion are new Protection talents → hit-cap checks read Precision from talents.
- Skyborne races carry Wind Blessed (+1% haste) → empirical swing-timer estimation absorbs it; no config needed.

**Tooling checks this evening:** Warcraft Logs, softres.it, wago.tools, Raid-Helper — no Forever announcements found. Re-check daily through the first beta week.

## 2026-09-17 (beta day)

**Game facts that changed the plan**
- **Raids unlock Dec 9, 2026 (global).** Onyxia's Lair (40), Hyjal Summit (20), Barrow Deeps (10); bosses, entrances, attunements, tier sets all TBD. Launch is Nov 4 at 3 pm Pacific, so there are five raid-free weeks: leveling, dungeons (nine new), professions, recruitment. Roadmap Phase 4 now targets Dec 9.
- **Beta**: opens after today's 10:30 am PDT Q&A; level cap 20 for two weeks, then 30 until Oct 21. No raid or talent-cap testing in beta; nothing carries to live.
- **Early name reservation Oct 27–Nov 3** (up to three characters): the window to finalize the roster import with real character names.
- **Class rules that touch the metric engine**: Expertise replaces weapon skill (racial weapon skills removed); periodic damage can crit; Improved Battle Shout is baseline; Improved Slam at max rank removes the swing interruption; Alliance gets Shaman (Windfury Totem), so extra-attack collapsing applies to both factions. Hardcore ruleset promised "by winter". Rulesets (Normal/PvP/Hardcore) rather than realm identity are described in press; treat `realm` as free text until confirmed.

**Tooling**
| Dependency | Status | Action |
|---|---|---|
| Beta client datamine | **Available now.** Wowhead reports the beta client is open for datamining and has Forever talent and Legacy calculators, a database section, and a news webhook; daybreakforever.com lists abilities, talents, set bonuses, items new in the client | Items adapter: add Wowhead (reference/tooltips only), daybreakforever datamine, wago.tools (once the build is listed) as candidate sources; expect item IDs to be stable from beta to live but re-verify at launch |
| WoWSims Forever engine | **Exists (early).** `github.com/ElliotWood/Forever`, a fork of wowsims/classic with a `forever` ruleset branch; Warlock, Priest, Druid, Shaman converted so far; MythicSim hosts it as a Quick Sim at mythicsim.com/wow-forever/sim, droptimizer to follow once beta gear/loot tables exist | Module F Layer A: plan on this engine (WASM build) instead of the EP fallback; track which classes are implemented; treat results as directional until verified against beta |
| Talent data | Talents Forever rebuild from the beta client is scheduled today (site still shows the pre-beta demo data); a second MIT-licensed dataset exists at `github.com/Deradon/wow-forever-talent-calc` (469/470 talents, rank-1 only from footage) and is what the WoWSims fork vendors | Keep Talents Forever as primary (CC BY, per-rank text); add Deradon as a fallback source in the talents adapter; expect a snapshot with a new `generated` date within a day |
| Warcraft Logs Forever host | **Not announced** | Unchanged: `WCL_API_HOST` config, build on Era |
| softres.it Forever zones | **Not added.** Note: softres.it has moved to a rebuilt site (legacy.softres.it kept) and added "Raid Series" with Bad Luck Protection | Re-verify the reverse-engineered create flow against the rebuilt site before Phase 2; evaluate Raid Series/BLP against Module B's forecasting and priority rules (it may replace part of them for PUG-style teams) |
| Blizzard API namespace | none | unchanged |
| Fojji Forever pack | none | unchanged |
| Raid-Helper Forever templates | not checked | create templates by zone size (10/20/40) ourselves |

## 2026-09-15 (announcement +3 days)
- All Forever tooling unconfirmed; Talents Forever demo data only; temple-era softres flow documented; WCL v2 API docs adopted.
