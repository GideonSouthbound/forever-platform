# Module E · Boss Guide

**Purpose:** a flip-through guide per boss that is generated from logs, annotated by officers, animated with role tokens, and exported to in-game reminders. Tables: `boss_guides`, `boss_abilities`, `strats`, `reminder_exports`.

## Generated content
- Ability list per boss from WCL casts: name, casts per pull, avg damage, deaths attributed (tank/raid), lethality rank. Officers add one line per ability ("what to do").
- "What actually kills us": lethality + cascades (Module C), refreshed nightly from own logs; public logs bootstrap before first pulls.
- Special seats: named mechanic roles (e.g., a Burning-Adrenaline-style handler, orb controller, decursers) with criticality → consumed by Module D.

## Strat pages
`strats.layout` is a schematic room drawn by officers (polygons/circles), never Blizzard map art. `strats.phases[]` hold token positions, paths, and callouts per phase (see `07-strat-format.json`). Tokens colored by role: tank, melee, ranged, healer, special (named). Renderer: SVG with keyframe interpolation and a scrubber; editor is the same component in edit mode (drag tokens, add keyframe, add callout). JSON-authored strats ship before the editor.

## Modes
- Flip-through (phone-first): one screen per phase; top-3 lethal mechanics pinned.
- Pre-pull briefing generator: 60-second read-aloud assembled from lethality, special seats, and positions.
- In-game reminder export (adapter; see `12-in-game-ui-alternatives.md`), targets in priority order: Northern Sky Raid Tools reminder set (per-boss text/TTS/glow, shared in-addon) if NSRT runs on Forever; Method Raid Tools note text (always available, plain text); DBM/BigWigs custom bars; `/rw` macro text block. WeakAuras is a conditional target only — the WA project halted development for the Midnight API (see `11-dependency-status.md`). Regenerated on edit and versioned in `reminder_exports` (`kind` names the target).

## Acceptance
- Every boss with ≥ 10 ingested pulls shows a generated ability table with lethality ranks.
- A JSON strat renders and animates; edits create a new `version`.
- Briefing text is deterministic and under 120 words; the reminder export validates in whichever target addon the beta confirms (DBM notes at minimum).
