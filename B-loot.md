# Module B · Loot

**Purpose:** the loot sheet is generated, never maintained. Tables: `items`, `loot_configs`, `wishlists`, `soft_reserves`, `loot_awards` (append-only), `loot_sheets`, `loot_forecasts`.

## Inputs
- Wishlist rank per character (members edit; auto-mark received from awards).
- Soft reserves imported from softres.it at T-2h and raid start.
- Attendance % over the team's window; items received in the last N lockouts (recency penalty); main vs alt; BiS tag by role/spec; officer overrides.
- Gear from logs (Module F): SR sanity check flags reserves on items the player already wears.

## Engine (per team config)
Methods: `sr_roll` (launch default; softres handles reservation, we handle tie-breaks and eligibility), `priority_points` (attendance-weighted with restricted-item thresholds), `council` (officer votes in the web UI). No gold-based method exists and none may be added: GDKP is banned in Forever (Blizzard, Sep 17, 2026) and the platform never models gold. Output per item: ordered candidates with reasons ("SR + 92% attendance + no loot in 3 weeks"). Sheet columns: Item · Boss · SR'd by · Priority order · Reason · Last awarded to/when. Export `.xlsx` (SheetJS) + web table + Discord post to officers.

## Awards
Paste Gargul award export → `loot_awards` rows (source `gargul`); manual entry allowed; corrections are new rows with `superseded_by`. Loot history per character is member-visible; a "loot drought" indicator appears on the sheet. Dispute log attaches ledger evidence.

## Forecasting
Expected drops per boss per week (from drop tables when known, else observed frequency in ingested logs) vs wishlist contenders → `weeks_to_satisfy` per item; surfaced on wishlist pages and to recruitment ("don't recruit a 5th rogue while daggers are contested").

## Gating
Per-boss resist/gear thresholds checked from logged gear; roster builder shows who fails.

## Acceptance
- T-2h job produces the sheet with reasons for every listed item and posts it.
- Awards round-trip: Gargul paste → ledger → wishlist marked received → next sheet reflects recency.
- Forecast page shows contenders and weeks-to-satisfy for every wished item.
