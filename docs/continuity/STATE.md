# GrowthTwin — current handoff

Last verified: 2026-09-29 11:32 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` at `f31c16b` (PR #102); docs PR #101 and workspace model PR #102 are merged. Post-merge main CI run `36543340617` was still running at this snapshot.
- PR #100 CI run `36541396010` and post-merge main CI run `36541595990` passed. PR #101 CI `36542515905` and PR #102 CI `36543083676` passed, including Django tests, formatting/lint, and browser E2E.
- Local development site is listening at `127.0.0.1:8002` (PID 11876). It serves the current source after collecting static assets and restarting the verified runserver.

## Product and safety context

- GrowthTwin targets people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability reference, not first-release scope.
- Local product development with synthetic data is authorized. Keep Django 5.2/PostgreSQL modular monolith; use feature branches and PRs; do not push directly to `main`.
- The site demonstrates brief → plan/preview → deterministic editable copy → simulated pause → sample report. Anonymous session drafts are stored in PostgreSQL. No AI provider, ad account, publication, real spend, or real metrics are connected. Do not enter real or sensitive data.
- The Heroku `clearsessions` job's first run succeeded, but Scheduler is best-effort and its actual one-off dyno cost is unverified. It is not a real-data retention guarantee. Staging E2E, backup/restore, rollback, and final cost/CI recording remain gates before external beta or production.
- First advertiser workflow/destination, production AI/data terms, category-specific retention, and real-data admission remain undecided. Do not connect accounts, publish, spend, deploy production, or add paid services without the required authorization.

## Recent verified work

- Phase 1 acceptance was verified against the brief → preview → sample report journey. Manual desktop review at a 1252 px viewport found horizontal page overflow, a hard-to-read data-use notice, and a report action that could leave the report off-screen. PR #100 fixed all three; the refreshed desktop view had no horizontal scrollbar and the report was visible after navigation. Mobile remains covered by E2E.
- PR #96 corrected the first-visit data notice: inputs go to the GrowthTwin app and are stored as a temporary session draft; this prototype does not send them to AI services or ad platforms, publish, or spend.
- Two synthetic advertiser briefs and the existing-draft edit flow were reviewed. Plan/copy reflect supplied facts, and edited copy remains visibly stale until the advertiser chooses to regenerate it. No other defect was demonstrated.
- A local browser test attempt could not create its PostgreSQL test database because the configured local DB role lacks `CREATE DATABASE`; it did not run. The complete required CI suite passed on PR #100 and after merge.
- [ADR-0007](../adr/0007-workspace-ownership-and-retention.md) establishes a synthetic-only Phase 2 boundary: future campaign data is workspace-owned, anonymous drafts are not backfilled, and real-data retention must be defined by data category and purpose before launch. It is not legal approval to process personal data.
- PR #102 added the minimal `Workspace(owner, name, created_at)` model, user deletion cascade, migration, and owner-scoping tests. The model is not yet used by signup or campaign UI. Django system check, migration consistency, Ruff lint/format, and PR CI passed. Local focused tests could not start because the configured PostgreSQL role lacks permission to create the test database.

## Next action

Add a minimal authenticated workspace entry point with server-side owner filtering and workspace creation/listing tests. Keep anonymous session drafts separate and use synthetic data only; do not set a universal retention duration.
