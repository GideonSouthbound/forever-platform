# Module G · Recruitment & Retention

**Purpose:** public team pages that write themselves, an application pipeline that lands in Discord, and retention signals that trigger care instead of silence. Tables: `applications`, `trial_scorecards`, `retention_flags`.

## Public pages (`/teams/<slug>`)
Requirements, raid days/times in the viewer's timezone, open roles computed from roster vs template (and loot forecast contention), loot rules summary, a guild-rules block (default text: no GDKP, no gold buying, no paid carries — matching Blizzard's Forever policy), progression timeline, screenshots. Onboarding (Module H) can ask new members to acknowledge the rules block.

**External listing:** forevercommunity.org is a community-run Forever guild finder (guild pages with openings and schedules, player profiles, applications, forum; Discord login). List each team there and link back to its own page; treat it as a lead source into the pipeline below, and as prior art worth reading before building the public pages.

## Applications
Form (class/spec, availability, log profile link, questions with conditional follow-ups) → `applications` → Discord thread in the officer channel with a summary embed → status pipeline (new / trial / accepted / declined) → role sync on accept. **Auto-screen:** log profile → parses, spec, gear → `screen` card on the application. With Forever Logs this needs `events:read` plus a way to find an applicant's reports, and no character-level endpoint is documented; until one exists, the card shows the profile link and the applicant's answers for officers to read. Warcraft Logs profiles from other game versions can still be screened through the `wcl` adapter.

## Trials
Week-4 scorecard: attendance, band-relative parses, reliability, mechanic deaths, recommendation; officers vote in the thread.

## Retention
Quiet-member flow: 3 weeks with no signups → check-in (bot DM or officer task), not a demotion; rank steps down later with one-click return. Attendance-decay alerts to officers. Alumni page for retired members.

## Acceptance
- Team page open-roles line changes when a roster/template changes.
- An application creates a thread with a screen card within a minute.
- Scorecard generates at week 4 with data from Modules A and C.
