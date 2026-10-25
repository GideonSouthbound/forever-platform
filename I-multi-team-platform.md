# Module I · Multi-team & Platform

**Purpose:** 2–3 guilds under one login and one Discord; jobs, status, backups, and exports that keep the whole thing running for years. Tables: `orgs`, `teams`, `team_memberships`, `jobs`, `api_calls`, `integration_status`, `audit_log`, `settings`, `exports`.

## Tenancy
Org → teams → characters; users can raid on Team A's main and Team B's alt; characters transfer between teams with history intact. Forever is realmless: a team is defined by ruleset + faction (+ region), and both are hard walls for grouping, so placement and roster tools only consider characters matching the team's ruleset and faction; names are two-part and unique per region. "All teams" dashboard for org leadership: progression, attendance, open roles, upcoming raids, integration status. Guest-raider pool spans teams.

## Roles & scopes
`org:admin`, `team:lead`, `team:officer`, `team:raider`, `team:trial`, `team:applicant`, feature scopes (`softres:access`, `loot:manage`, `reviews:view_all`). tRPC middleware; bot mirrors from Discord roles; nightly reconciliation report.

## Jobs & status
Idempotent, resumable jobs with cursors; `/admin/jobs` page; integration health every 15 min; "needs attention" board for raid leads.

## Data ownership
Nightly `pg_dump` to R2 (30-day retention), raw event archives to R2, one-click org export and per-member export/delete, quarterly restore drill logged in the runbook.

## Observability
Sentry; structured logs; `api_calls` with points cost; alerts on log-API quota exhaustion (Forever Logs per-minute and daily limits), failed raid-create steps, and poller failures.

## Acceptance
- A user with characters on two teams sees both; officers of Team A cannot see Team B officer data unless org admin.
- Killing the worker mid-job and restarting resumes without duplicate API calls.
- Restore drill from last night's backup succeeds in a staging database.
