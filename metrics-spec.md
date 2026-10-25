# Metric Engine Specification

All times in milliseconds relative to fight start (`fight.startTime`). All metrics are numbers with units. One JSONB vector per (report, fight, player).

## 1. Event preprocessing

1. Resolve ability names: map every `abilityGameID` via the report's `masterData.abilities` (gameID → name). Work with names from here on; keep IDs for debugging.
2. Restrict to the player's `sourceID`. Restrict damage to `targetID` = the boss actor(s) named in `boss-config.json` (`boss_actor_names`). Damage to other targets is stored separately as `padding_damage`.
3. Player death time = first `Deaths` event for the player (if any). Time alive = death time or fight end.
4. Build the **CC timeline** for the player: intervals where a debuff named in `boss-config.json` `cc_debuffs` (or a global list: any debuff whose name contains "Fear", "Stun", "Sleep", "Polymorph", "Mind Control") is active on the player (from `Debuffs` events where the player is the target; in the API, request `Debuffs` with `targetID` = player if `sourceID` filtering excludes them — verify via introspection).
5. Build **forced-movement windows** from boss casts listed in `boss-config.json` per boss: `[castTime, castTime + window_ms]`.

## 2. Swing detection (melee and hunters)

**A swing event** is any `DamageDone` event where the ability name is `Melee` **or** an on-next-swing ability: `Heroic Strike`, `Cleave`, `Maul`, `Raptor Strike`. Include misses, dodges, parries, blocks, and glancing blows: these still carry a `hitType`; count them. For hunters, the swing ability is `Auto Shot`.

**Extra attacks:** Windfury, Sword Specialization, Hand of Justice, and similar produce additional `Melee` events with the same timestamp (or within 50 ms) as a real swing. Collapse any cluster of Melee events within 50 ms into one swing; record `extra_attacks` = collapsed count.

**Dual wield:** off-hand swings are separate `Melee` events with their own timer. Detection: if the parse has two distinct stable interval clusters (see §3), treat the player as dual-wielding and analyze main-hand and off-hand separately (off-hand swings are not preceded by on-next-swing abilities). For the PoC, if separation is ambiguous, analyze the combined stream and flag `dual_wield_ambiguous = true`.

## 3. Empirical swing timer

For the main-hand stream:
1. Compute inter-swing intervals `Δ` between consecutive swings.
2. Discard intervals during CC, forced-movement windows, or after death.
3. The **base timer** is the mode of `Δ` after rounding to 50 ms, restricted to the plausible range 1,400–3,800 ms (Auto Shot: 1,500–3,500 ms). Use a histogram; take the tallest bin among bins with ≥ 5% of intervals.
4. **Haste-adjusted timer** over time: while a haste buff from `boss-config.json` `haste_buffs` (e.g., `Flurry`, `Kiss of the Spider`) is active, the expected timer is `base × (1 − haste_pct)`. If haste percentages are unknown for a buff, estimate from the parse: mode of intervals during that buff's uptime.
5. Sanity: if fewer than 20 usable intervals, set `swing_timer_confidence = low` and skip swing attribution in the review (state "insufficient swing data").

## 4. Metrics

### 4.1 Swing efficiency (melee, hunters)
- `swings_actual` — collapsed swing events on the boss.
- For each interval `Δ` between consecutive swings (and from fight start to first swing, and from last swing to end-of-alive), with expected timer `T` at that time: `lost = max(0, floor((Δ − 1.15·T) / T))`. (The 15% tolerance absorbs latency and parry-haste noise.)
- `swings_expected = swings_actual + Σ lost`.
- `swing_efficiency = swings_actual / swings_expected`.
- **Gap classification** for each interval with `lost ≥ 1`:
  - `dead` if after death time,
  - `cc` if ≥ 50% of the gap overlaps the CC timeline,
  - `forced_movement` if ≥ 50% overlaps a forced-movement window,
  - else `unexplained`.
- Store `lost_swings_by_cause` = `{dead, cc, forced_movement, unexplained}` and `unexplained_gaps` = list of `{start, duration_ms, lost}` (top 5 by duration for the review).
- `avg_swing_damage` = mean damage of landed swings (hits + crits + glancing).
- `lost_damage_avoidable = lost_swings_by_cause.unexplained × avg_swing_damage`.
- `parries`, `dodges`, `misses` — counts by `hitType` on swings. Parries imply front-facing; report the count.
- `slam_clips` (warriors): count of intervals < 0.85·T immediately following a `Slam` cast. Note in the review that Slam resets the swing timer in Era.

### 4.2 Activity
- `active_time_pct` — union of `[t, t + 1500]` for each cast plus `[t, t+T]` for each swing, divided by time alive. Matches the spirit of WCL's "active time".
- `gcd_idle_ms` — time alive minus the union of `[t, t + 1500]` over all `Casts` (instants included) and minus CC time. `gcd_idle_pct` = `gcd_idle_ms / time_alive`. (Melee swings don't consume GCD; this is a proxy and is labeled as such.)

### 4.3 Uptimes (per spec, names from `boss-config.json` `tracked_uptimes`)
For each tracked buff/debuff: percentage of time alive the aura is active on the relevant target (debuffs on boss from any source for raid debuffs like `Sunder Armor`; from this player only for personal ones like `Rend`, `Slice and Dice`, `Rupture`).

### 4.4 Cooldowns (per spec, `tracked_cooldowns`)
- `<name>_casts` — count.
- `<name>_first_use_ms` — time of first cast.
- `<name>_possible` = `1 + floor((time_alive − first_use_ms) / cooldown_ms)` using the cooldown from config; `<name>_usage_pct = casts / possible`.
- **Loatheb alignment:** `<name>_spore_overlap_pct` — share of the cooldown's active duration that overlaps `Fungal Bloom` on the player.

### 4.5 Consumables and buffs at pull
From `CombatantInfo` auras at fight start: count auras whose names appear in `consumes.json`, by category (`flask_elixir`, `food`, `juju`, `weapon`, `protection_potion`, `world_buff`). Store `consumes_present` (names), `consumes_missing_expected` (names from the spec's `expected_consumes` list not present), `world_buffs_count`.

### 4.6 Outcome
- `dps_boss` — damage to boss / time alive. `dps_total` — all damage / fight duration (WCL's number).
- `deaths` (0/1), `time_alive_pct`.
- `rank_percent` — from the report's `rankings` payload for guild players; from band membership for reference parses.

## 5. Bands and attribution

**Kill-time buckets:** by fight duration: `<2:00`, `2:00–3:30`, `3:30–5:30`, `>5:30`. A parse is compared only within its bucket. If a bucket has `n < 20` for a band, fall back to the adjacent bucket and mark `bucket_fallback = true` in the review.

**Bands:** for each boss × spec × bucket × band ∈ {75–94, 95–98, 99+}: per metric, `median`, `mad` (median absolute deviation), `n`. Guild players below the 75th percentile are compared against the 75–94 band as "next band" and get "strengths" computed against the pooled 50–74 band if available, else against their own previous kills.

**Attribution to the next band** (simple, explainable; no ML in the PoC):
1. For each metric `m` with a defined direction (higher-is-better or lower-is-better, declared in `boss-config.json` `metric_directions`), compute the standardized gap `z_m = (band_median_m − player_m) / max(mad_m, ε)` in the improving direction; negative z means the player already beats the band median → candidate strength.
2. Weight: `w_m` from a fixed table in `boss-config.json` `attribution_weights` (swing efficiency, consumes, uptimes, cooldown usage, gcd idle). These are hand-set priors for the PoC; a fitted model replaces them later.
3. Contribution `c_m = max(0, z_m) × w_m`; normalize contributions to sum to 100% of the gap.
4. **Expected gain** in percentile points for closing metric `m` to the band median: `gap_points × c_m`, where `gap_points = next_band_lower_bound − player_percentile`.
5. **Ease** class per metric category: consumes = 1, swing/uptime/cast-order = 2, cooldown alignment = 2, positioning (parries) = 2. Rank candidate changes by `expected_gain / ease`; take the top 3 for the focus block.
6. **Strengths:** metrics with `z_m ≤ −1` versus the *lower* band (or vs. own history), top 2.
7. **Ceiling line:** the 95–98 band's median `dps_total` for the bucket, and a coarse split of the gap into "gear" (proxy: the residual after behavior metrics) and "behavior" (sum of contributions). Label as an estimate.

## 6. Review rendering

### 6.1 Technical block (deterministic templates)
```
{Boss}, {date} · {Spec} · kill {m:ss} · your parse: {pct}th percentile ({band}), comparable kills n = {n}{bucket_fallback_note}
What held against the {lower_band}: {strength_1}. {strength_2}.
Gap to {next_band}: {gap_points} percentile points. Attribution: {item_1 name} {pct}% ({detail}), {item_2}..., {item_3}...
This week: 1) {change_1} (expected +{gain} points). 2) {change_2}. 3) {change_3 (optional)}.
Swings: {actual} of {expected} possible ({eff}%). Lost {lost_total}: {cc} CC'd, {forced} forced movement, {unexplained} unexplained gaps averaging {avg_gap} s ≈ {lost_damage} damage ≈ {points} percentile points. {parries} parries detected.{slam_clip_note}
Ceiling: {band_95} runs {dps} DPS on this kill length; current gap decomposes as gear ≈{g}%, behavior ≈{b}% (estimate). Not a target for this week.
Trend: {n_fights} fights, {delta:+d} points since {date}; last focus item ({name}) moved {before} → {after}.
```
Omit any line whose data is missing; never print placeholders.

### 6.2 Plain-language paragraph (rules enforced by a linter)
- 3–5 sentences. At most **one** number in the whole paragraph. One action verb sentence ("do X").
- Names only the single largest avoidable loss and the single easiest win.
- Vocabulary map: uptime → "keep hitting the boss"; GCD idle → "gaps where you weren't pressing anything"; parry → "the boss blocked hits because you were in front of it"; percentile/band → "move up a color".
- Banned words: unfortunately, bad, poor, great, amazing, unlucky, lazy, should have, obviously, easy, just.
- No comparisons to named people. No exclamation marks.

Template skeleton:
```
You lost about {fraction_words} of your swings on this kill, mostly {where_words}. {one_action_sentence}. {second_easy_win_sentence}. Everything else can wait.
```
Where `fraction_words` is a spoken fraction ("one in seven"), `where_words` comes from the largest unexplained-gap cluster's timing relative to boss casts ("right after the spore waves", "during the transitions"), and the action sentences come from the top two focus items.

## 7. Lethality (per boss)

From `Deaths` events for all players in all ingested fights of the boss:
- Per killing-blow ability: deaths, deaths per pull, share of tank deaths (tank = took ≥ 40% of the boss's melee damage in that fight).
- **Cascade:** ≥ 3 deaths within any 5-second window. Attribute to the most recent boss cast (any boss ability, from `Casts` with the boss as source) before the first death of the cascade, within 10 s.
- **Healer gap** for tank deaths: ms since the last heal landed on the tank before death (from `Healing` events targeting the tank). Stretch goal.
