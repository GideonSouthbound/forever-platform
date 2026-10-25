# Module J · Spreadsheet imports (Excel/CSV → pending records)

**Purpose:** leadership runs on spreadsheets today. Any sheet they already maintain can seed the platform without retyping, and everything imported lands in a **pending** state until a real person or an officer confirms it. Tables: `roster_imports`, `roster_import_rows`, `seat_assignments`, plus `status`/`claimed_by` columns on `characters` and `team_memberships`.

## Import kinds
| Kind | Sheet looks like | Creates (pending) | Confirms when |
|---|---|---|---|
| Roster | one row per character: name, class, spec, role, team, main/alt, Discord handle, notes | `characters` (status `pending`), `team_memberships` (status `pending`), social edges if a "plays with" column exists | the Discord user claims the character in onboarding (name/handle match) or an officer confirms |
| Raid-night roster | groups/rows of names by role for a date and zone | `raid_events` (planned) + `seat_assignments` (status `pending`, source `import`) | the player signs up in Raid-Helper (auto-match) or accepts the bot's DM; unconfirmed seats show as gaps at T-24h |
| Wishlists | character × item rows or a matrix | `wishlists` rows (rank from column order) | immediately, but flagged `imported` until the member edits once |
| Availability | character × weekday grid | `availability` rows | immediately |

## Flow
1. Upload `.xlsx`/`.csv` (SheetJS parses client-side; server re-validates). Officers can also download a template per kind.
2. **Column mapping UI:** auto-detect headers by synonyms (Name/Character/Toon; Class; Spec/Talents; Role/Position; Team/Guild/Group; Main/Alt; Discord/Tag). Mapping is saved per org so re-imports of the same sheet are one click.
3. **Validation:** class/spec/role vocab (per patch), team slugs, duplicate names (with realm), items resolved by name against `items`, Discord handles normalized. Row-level errors, never a failed import.
4. **Preview/diff:** for each row: create / update / skip / error, with the fields that would change. Existing records match on character name (+ realm); re-importing a sheet updates rather than duplicates.
5. **Apply:** writes pending records and an audit entry; produces a summary post in the officer channel ("42 characters imported, 31 already claimed, 11 pending").
6. **Claims:** onboarding DM matches a new Discord user to pending characters by handle, then by exact name, then offers a pick-list; officers see "unclaimed" with a nudge button. Pending memberships become active on claim; role sync follows.

## Raid-night specifics
- A raid roster sheet creates the Raid-Helper event too (Module A W1) and the bot DMs pre-assigned players a signup link; the roster builder shows imported seats as "pre-assigned (unconfirmed)" until their signup arrives, then matches automatically.
- Seat rows keep `source` (import | solver | manual) so Module D's suggestions and officer edits are distinguishable.

## Round trip
Export the current roster, a raid roster, wishlists, or availability back to `.xlsx` with the same columns, pending rows flagged, so leadership's spreadsheet habit keeps working while the platform becomes the source of truth.

## Rules
- Nothing imported becomes visible to members as "theirs" until claimed.
- Imports are idempotent and reversible: each import can be rolled back (rows carry the import id; rollback removes only records the import created and still pending).
- No hidden overwrites: updates to active records require the diff to be accepted per field.

## Acceptance
- Importing the guild's current roster sheet creates pending characters and memberships with zero duplicates on re-import.
- A new Discord member with a matching handle auto-claims their character during onboarding.
- A raid roster sheet creates a planned raid with pending seats, the RH event, and DMs; a Raid-Helper signup confirms its seat without officer action.
- Rollback of an import removes exactly its still-pending records.
