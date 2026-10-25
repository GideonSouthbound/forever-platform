# 01 · Architecture

**Updated 25 Oct 2026:** combat logs come from Forever Logs (REST, `13-forever-logs-api.md`), so the `wcl.*` jobs are now `logs.*`; Warcraft Logs stays behind the same `logs` adapter for the optional poc. Attunement checks (Module A W6) run inside the roster builder; they need no job.

## 1. System shape

```mermaid
flowchart LR
  subgraph Discord
    RH[Raid-Helper bot]
    Bot[apps/bot]
  end
  subgraph Web["apps/web (Next.js on Vercel)"]
    UI[Pages]
    API[tRPC + /api/bot/* + /api/cron/*]
  end
  Worker[apps/worker: ingest, pollers, reports]
  DB[(Postgres)]
  R2[(Object storage: backups, exports, raw event archives)]
  subgraph Ext[External]
    RHapi[Raid-Helper API]
    SR[softres.it]
    LOGS[Forever Logs REST API]
    TF[talentsforever.com JSON]
    WAGO[wago.io]
    ITEMS[Item data source(s)]
  end
  Bot -->|bearer| API
  UI --> API --> DB
  Worker --> DB
  Worker --> LOGS & TF & WAGO & ITEMS
  API --> RHapi & SR
  Worker --> R2
```

- **The bot is stateless.** It calls `apps/web` routes with a bearer token; all state lives in Postgres. It never has its own database.
- **The worker owns anything long-running or scheduled.** It starts as cron routes inside `apps/web` and is split into `apps/worker` the first time a job exceeds the platform's request timeout (log ingest will).
- **Every external system has one adapter** in `packages/integrations/<name>` exposing a small interface, a fixture-recording mode, a health check, and a manual-fallback path documented in the UI.

## 2. Tenancy and roles

- `orgs` (one community) → `teams` (in-game guilds) → `characters`. Users are org-level; memberships are team-level.
- Scopes: `org:admin`, `team:lead`, `team:officer`, `team:raider`, `team:trial`, `team:applicant`, plus feature scopes (`softres:access`, `loot:manage`, `reviews:view_all`). Checked in tRPC middleware; the bot mirrors them from Discord roles and re-syncs nightly.
- One Discord server per org. Per-team channels (signup, officer, SR-token thread, ui-updates) are configured in `teams`, never hardcoded.
- Everything is `org_id`-scoped from the first migration even though there is one org. That is discipline, not a SaaS plan.

## 3. Jobs

A `jobs` table (name, status, progress cursor, resume_at, error) and a runner that is idempotent and resumable. Job kinds:

| Kind | Trigger | Notes |
|---|---|---|
| raid.create pipeline | user action | steps recorded individually; partial failure → "needs attention" checklist |
| signups.sync | every 5–10 min for open events | snapshots for timeline and no-show analysis |
| reminders | T-24h, T-2h | per-team settings |
| loot.sheet | T-2h | SR import + engine + xlsx + Discord post |
| logs.ingest | on paste of a report link (Phase 4); auto-attach only if a guild-scoped listing appears | report, encounters, actors, events; raw events archived on first read (rolling retention); needs `events:read` |
| logs.stats.sync | weekly | `/statistics` percentile tables per boss × spec × bracket (ETag-cached); explicit `difficulty` |
| bands.build / standards.build | weekly | after sampling |
| reviews.generate | weekly for opt-in players | technical + plain |
| lethality.build | nightly | per boss |
| talents.poll / wago.poll / items.poll | hourly / hourly / daily | snapshot adapters |
| digest.weekly | Sunday | upcoming raids, gaps, loot, parses, attendance |
| backup.nightly / export.on_demand | nightly / user | R2 |
| integration.health | every 15 min | status board |

Rate limits: Forever Logs limits are per key, per minute and per day; each job budgets its calls and stops at 85% of the daily quota, honours `Retry-After` on 429, and resumes. Event pages use the largest `limit` the job can hold, because cost is per request. Raid-Helper and softres calls are low-volume; softres gets exponential backoff and a per-event idempotency key.

## 4. Data flow in one raid week

1. Sun: digest posts upcoming raids and signup gaps; recruitment page updates from roster vs template.
2. Mon–Wed: signups sync; roster builder shows role counts and bench candidates; placement tool is consulted if a team is short or overfull.
3. T-2h: SR import → loot sheet → officer post.
4. Raid: control room view; late detection from voice presence; wipe autopsy only if a live-logging source exists.
5. After: attendance credits from signups and voice presence (MVP), or from a pasted Forever Logs report (Phase 4) → signups-vs-attendees; Gargul award export → loot ledger → wishlists updated.
6. Weekly (Phase 5): stats sync → bands → reviews to opt-in players → coaching queue for officers.

## 5. Security

- Encrypt at rest: softres admin tokens, Raid-Helper API keys. The Forever Logs key lives only in the secret store and travels only in the `Authorization` header (the API rejects keys in query strings); share only its `alog_` prefix.
- Never log query strings that can carry tokens; strip before error messages.
- Bearer auth bot↔web; keys rotated via the secret store.
- Audit log on every officer-facing mutation; soft deletes.
- Member data export and delete on request (GDPR-style), even though we're a private community.

## 6. Longevity

- Nightly `pg_dump` to R2 with 30-day retention; quarterly restore drill.
- Every derived table keyed by `patch`; a content patch adds config, never edits history.
- Reference bands and standards rebuild weekly and keep prior versions.
- Dependency updates automated with CI; framework majors pinned.
- Runbook covers: rotating each secret, re-authorizing the bot, moving hosts, restoring a backup, handing over admin.
