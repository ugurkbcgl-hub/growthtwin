# GrowthTwin — current handoff

Last verified: 2026-09-30 20:17 +0300 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Latest `main` baseline: `1253730d6d6bf5a3ca9b371862999e3040a6d75a` after PR #175. PR #175 required CI `36749727263` and post-merge CI `36750049089` passed, including Django tests and browser E2E. PR #174 also passed required CI `36748631258` and post-merge CI `36748897583`.
- `main` branch protection is enabled: required check `Django system check`, up-to-date PR branches, and admin enforcement.
- Current branch: `docs/phase0-final-handoff`, prepared from the verified main for this continuity refresh. Check live PR/CI status before further work.
- Heroku dashboard on 2026-09-30 shows the latest code deployment as v5 / `ac2f627d` dated 2026-09-27; later v6–v10 entries were configuration releases. `/health/` returned HTTP 200 and database-ready, with `version: unknown`.
- Heroku Resources shows one Basic dyno, Essential-0 Postgres, Standard Free Scheduler, and an estimated USD 12/month. This is not an invoice; actual tax/usage and one-off Scheduler dyno cost remain unverified.

## Completed

- Reviewed deployment/testing docs, ADR-0003, staging E2E runner, CI, GitHub branch protection and the live Heroku dashboard.
- Added a Phase 0 staging verification sequence, refreshed deployment/roadmap facts, and merged PR #175.
- `git diff --check` passed; required/post-merge CI passed. No staging E2E, deploy, account creation, restore, rollback or resource change was performed.

## Open blockers

- The browser E2E runner needs a disposable synthetic account. The account credentials are not available here; never share the password in chat, Git or logs.
- Runtime health does not expose the deployed commit. Dashboard release `ac2f627d` is the target evidence; verify that it is still current before the E2E.
- Backup/restore and rollback remain unverified. A restore can overwrite the only staging database; first establish a safe target and recovery order.
- Keep all staging values synthetic. No real account, campaign, publication, spend, or new paid resource was enabled in this review.

## Next action

Resume the staging profile-edit E2E only after a disposable synthetic account is identified. Run `python -m e2e.run_staging` from `apps/web`, entering credentials only at its hidden local prompts. If account/admin credentials are required, ask the owner to use the local prompt or provide access through a secure mechanism; do not request secrets in chat.

