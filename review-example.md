# Example review (target output shape)

Below is what one review should look like once the pipeline works. Numbers are illustrative; the shape, order, and tone are the spec. A casual player should be able to read only the last paragraph.

---

**Patchwerk, Sep 20 · Fury Warrior · kill 2:41 · your parse: 68th percentile (blue), comparable kills n = 47**

**What held against the 50–74 band:** Rend uptime 84% (band median 71%). Death Wish 1 use (band 0.9).

**Gap to 75–94 (purple):** 11 percentile points. Attribution: swing efficiency 46% (86% vs band 94%), consumes 31% (missing Juju Power, Winterfall Firewater), Heroic Strike queue 14%, Sunder timing 9%.

**This week:** 1) Add Juju Power + Winterfall Firewater (expected +3 points). 2) Close the swing gaps after the Hateful Strike swaps (expected +5 points).

**Swings:** 118 of 137 possible (86%). Lost 19: 0 CC'd, 0 forced movement, 19 unexplained gaps averaging 3.6 s ≈ 3,100 damage ≈ 5 percentile points. 4 parries detected.

**Ceiling:** the 95–98 band runs 1,540 DPS on this kill length; current gap decomposes as gear ≈ 44%, behavior ≈ 56% (estimate). Not a target for this week.

**Trend:** 3 fights, +9 points since Sep 6; last focus item (Rend) moved 61% → 84%.

---

**In plain terms:** You lost about one in seven of your swings on this kill, mostly in short stretches where you weren't hitting the boss and didn't need to be moving. Get back on him the moment the tank swap happens, and stay behind him so your hits don't get blocked. Bring Juju Power and Firewater next week and you'd likely move up a color. Everything else can wait.

---

## Linter checks the plain paragraph must pass
- 3–5 sentences; at most one number; one action sentence.
- No banned words (unfortunately, bad, poor, great, amazing, unlucky, lazy, should have, obviously, easy, just).
- No names of other players; no exclamation marks.
- Same input → identical text.
