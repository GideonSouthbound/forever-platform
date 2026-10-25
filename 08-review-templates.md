# 08 · Member-facing text templates and linter rules

All member-facing text is generated from a fact table by deterministic templates. See `poc/metrics-spec.md` §6 for the review templates. Rules below apply to every template.

## Tone rules (enforced by tests)
- Matter-of-fact. No adjectives of judgment, no praise words, no exclamation marks.
- Compare to bands or the player's own history; never to named players.
- One focus block, max three items. The ceiling is stated once as context, never as the ask.
- Plain-language closer: 3–5 sentences, ≤ 1 number, one action, names the single largest avoidable loss and the single easiest win.
- Banned words: unfortunately, bad, poor, great, amazing, unlucky, lazy, should have, obviously, easy, just.
- Vocabulary map: uptime → "keep hitting the boss"; GCD idle → "gaps where you weren't pressing anything"; parry → "the boss blocked hits because you were in front of it"; percentile/band → "move up a color".

## Templates
1. **Parse review** (technical block + swing block + plain paragraph): `poc/metrics-spec.md` §6, `poc/review-example.md`.
2. **Late nudge (DM):** "Raid started at {time}; you were marked late. If something came up, reply here and it's excused."
3. **Quiet-member check-in (DM):** "No signups in {n} weeks. Still with us? Reply with a thumbs up to keep your spot, or tell us what changed."
4. **Pre-pull briefing (read-aloud, ≤ 120 words):** "{Boss}. Top three: {m1}, {m2}, {m3}. Special seats: {seats}. Positions: {summary}. Go."
5. **Weekly digest:** sections in fixed order: Upcoming · Gaps · Loot · Parses · Attendance.
6. **Wipe autopsy:** "Wipe at {pct}%: cascade began with {ability} at {m:ss}, {n} deaths in {s} s, {k} to {ability2} {context}."

## Optional LLM rephrasing
Off by default. If enabled per org, the model receives only the fact table and the rendered template, may rephrase for readability, and the output is re-run through the linter; numbers must match the fact table exactly or the template text is used instead.
