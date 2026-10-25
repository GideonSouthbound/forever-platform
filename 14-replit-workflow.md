# 14 · Building with Replit

**Roles.** The Replit Agent writes the code. Claude owns the specs and reviews every phase at its gate. A GitHub repo holds the shared copy, so both always look at the same files. Nothing important lives only in a chat.

## One-time setup (no Git install needed on your computer)

1. **Unzip the package.** Inside is a folder called `forever-platform`. Upload what's inside it, so `README.md` sits at the top level of the repo.
2. **Create the GitHub repo.** On github.com: + (top right) → New repository → name it `forever-platform` → Public or Private → turn on the option to add a README so the repo isn't empty (ours replaces it). Public lets Claude pull it directly at review time; private works too, but attach a zip of the repo at each gate.
3. **Upload.** On the repo page: Add file → Upload files. Drag in everything from inside the `forever-platform` folder; GitHub keeps the folder structure (limit: 100 files per upload, 25 MiB per file; the package has about 50 files). Commit straight to the main branch with a message like "Spec package v2.1". Check that `README.md` shows at the top level.
4. **Import into Replit.** Go to replit.com/import → GitHub → connect your GitHub account (grant access to the repo if it's private) → pick `forever-platform` → Import.
5. **Find the Git pane.** In the Replit app: Tools → Git. It should show the GitHub repo. This is where the agent's work goes back to GitHub. The agent saves checkpoints as commits.
6. **Set a credit cap** in Replit before the first agent run.

## Every phase

1. In Replit, sync from the Git pane first, in case the specs changed since the last run.
2. Paste the phase prompt (Phase 1 below; later phases use the template). One phase per run.
3. When the agent asks for keys, add them under Secrets. Never paste a key into either chat.
4. When the agent stops at the gate, sync from the Git pane so GitHub has the new code.
5. Bring to Claude: "Phase N gate", the repo link (or a zip), and the agent's summary with its test output. Claude checks the code against the phase's acceptance criteria and the MVP gate list in `06-acceptance-tests.md`, then writes a fix list or the next prompt.
6. When a spec changes, upload the changed files to GitHub the same way (same names replace the old ones), then sync in Replit before the next run.

## Secrets by phase

| Phase | Secrets |
|---|---|
| 1 | Postgres connection (Replit's database provides it), Discord application credentials for login, Discord bot token, an auth session secret |
| 2 | Raid-Helper API key |
| 4 | Forever Logs API key (after `events:read` is granted) |
| Later | Object storage (R2) credentials for backups and exports |

## Phase 1 prompt

```
This repo is the full spec package for a WoW: Forever guild platform. Before writing code, read README.md, 00-BUILD_BRIEF.md, 01-architecture.md, 02-data-model.sql, 03-integrations.md, 05-roadmap.md, 06-acceptance-tests.md, 10-environments.md, test-data/README.md, and modules/I, J and H in full.

Build Phase 1 only (05-roadmap.md): tenancy, Discord login, teams with ruleset and faction stored as data (ours are Horde on rp_pvp; don't hardcode it), two-part character names, roster import from a spreadsheet into pending characters, claiming a character through the onboarding DM, and Discord role sync.

Use the stack in 00-BUILD_BRIEF.md section 3 (Next.js App Router, TypeScript, tRPC, Drizzle on Replit's Postgres, Auth.js with Discord, discord.js bot). If Replit makes part of that impractical, stop and write an ADR in docs/adr/ instead of switching.

Read keys from Replit Secrets only; never write a key into code or logs. Test against the fixtures in test-data/. The roster import and onboarding must pass the roster_import and onboarding checks in test-data/expected/walkthrough-expectations.json.

Stop at the Phase 1 gate. Run the tests and include the output, then summarize what you built, what's missing, and every deviation from the spec (also recorded in docs/adr/). Sync to GitHub. Do not start Phase 2.
```

## Later phases (template; Claude refines it at each gate)

```
Pull the latest specs, then read 05-roadmap.md (Phase N), the module specs that phase lists, 06-acceptance-tests.md, and every file in docs/adr/.

Build Phase N only. Keep the stack and the principles in 00-BUILD_BRIEF.md; every external system goes through an adapter with a manual fallback, no game IDs are hardcoded, and every derived row carries a patch. If something in the spec is impractical, stop and write an ADR instead of improvising.

Stop at the Phase N gate. Run the tests and include the output, then summarize what you built, what's missing, and every deviation from the spec (also recorded in docs/adr/). Sync to GitHub. Do not start the next phase.
```

## Hosting notes

- The web app and Postgres run natively on Replit.
- The Discord bot and the worker need a process that never sleeps: deploy them as a Reserved VM on Replit, or on Railway (see `00-BUILD_BRIEF.md` section 3).
- If a phase blows its budget without passing its gate, stop and fix the spec rather than pushing the agent.
