# GrowthTwin — current handoff

Last verified: 2026-09-30 20:12 +0300 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Latest `main` baseline: `05e102f26a5879d127914754128d1be08528c0db` after PR #174. PR #174 required CI `36748631258` and post-merge CI `36748897583` passed, including Django tests and browser E2E. PRs #171 and #172 also passed required and post-merge CI.
- GitHub `main` branch protection is enabled: required check `Django system check`, up-to-date PR branches and admin enforcement.
- Current feature branch: `docs/phase0-staging-live-review`; the dashboard findings and docs refresh are being prepared here. Recheck the live PR/CI before continuing.
- Heroku dashboard on 2026-09-30 shows the last code deployment as v5 / `ac2f627d` from 2026-09-27. Releases v6–v10 shown after it changed configuration. A direct `/health/` GET returned HTTP 200, database-ready, but `version: unknown`.
- The dashboard shows one Basic dyno, Essential-0 Postgres and Standard Free Scheduler; estimated monthly total about USD 12. This is not invoice evidence; tax and one-off Scheduler dyno costs remain unknown.

## Completed in this work

- Reviewed `DEPLOYMENT.md`, `TESTING.md`, ADR-0003, staging E2E runner, Phase 0 gates, CI and GitHub branch protection.
- Added the read-only Phase 0 verification sequence and refreshed deployment/roadmap records from the authenticated Heroku dashboard.
- `git diff --check` passed. No app tests, staging E2E, deployment, account creation, backup/restore, rollback or paid-resource change was performed.

## Open prerequisites

- No disposable synthetic staging account is verified for the existing profile-edit E2E. Runner `python -m e2e.run_staging` prompts for username/password locally; the password must be entered only at the hidden prompt, never in chat/Git/logs.
- Runtime health does not report a commit hash. The dashboard shows `ac2f627d`; verify it remains the intended target before testing.
- Backup/restore and rollback remain unverified. A restore can overwrite the only staging database; do not proceed until a safe target and recovery order are established.
- Actual invoice, taxes and Scheduler one-off dyno charges remain unverified. Do not add paid resources without a new owner decision.

## Next action

Identify a disposable synthetic staging account using the authorized admin path and run the existing staging browser E2E against the dashboard-verified `ac2f627d` release; enter credentials only in the runner's hidden local prompts. If credentials or admin access are needed, pause at that point rather than requesting them in chat.
