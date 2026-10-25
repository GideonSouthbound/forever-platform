# Module D · Placement ("carry budget")

**Purpose:** answer "which team can absorb which casuals/friends/family and still clear, while everyone has a good time." Officer-only. Tables: `player_profiles`, `team_capacity`, `placement_runs`, `social_edges`, `raid_templates.seats`.

## Inputs
- Per player: ceiling (Module F sim/stat-weight), execution ratio (Module C), reliability (mechanic failure rate from deaths/avoidable damage), attendance %, assignment history → **carry load** = gap to the seat's expected output weighted by reliability and attendance.
- Per team × zone: expected output = Σ(ceiling × execution) over the roster; requirement from boss HP/enrage (WCL-derived, public logs before first kill); healer and tank slack → **margin** and **carry capacity**.
- Seats from templates with **criticality** (low: 26th DPS; high: named mechanic seats from Module E's `special_seats`).
- Social graph: must_with / prefer_with / keep_apart edges collected at onboarding and editable by officers.

## Solver
Assignment problem: binary x[player, team, seat]. Constraints: one seat per player; class/role eligibility; high-criticality seats require reliability ≥ threshold; every team's expected output ≥ requirement × (1 + safety); must_with pairs same team; keep_apart different teams. Objective: maximize friends-together + prefer_with satisfaction + margin balance across teams (avoid dumping all carry load on one team). Implementation: javascript-lp-solver or glpk.js; greedy + swap local search as v1. Runs are stored with inputs, so decisions are auditable and reversible.

## Outputs
"Team B can absorb 3 more casual DPS and still clear Hyjal with 8% margin; Team A is at 1%." Per-player suggested seat with reason; bench fairness respects friend groups (never bench half a group). Guest-raider pool (alts/casuals) is drawn on when a team is short.

## Rules
Never expose carry loads or tiers to members. Members see assignments only. All numbers keyed by patch; profiles recompute weekly.

## Acceptance
- A run with 60+ players and 3 teams completes in < 5 s and satisfies all hard constraints.
- Changing one social edge re-runs and shows the delta.
- Capacity numbers reconcile with Module C bands and Module E requirements.
