# GrowthTwin — current handoff

Last verified: 2026-09-29 11:52 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Clean `main` at `16a5534` (PR #103); no open PRs. PR #101–#103 and their post-merge main CI runs passed; latest main CI is `36543676155`.
- PR #100 CI run `36541396010` and post-merge main CI run `36541595990` passed. PR #101 `36542515905`, PR #102 `36543083676`, and PR #103 `36543454240` CI passed, including Django tests, formatting/lint, and browser E2E.
- Local development site is listening at `127.0.0.1:8002` (PID 11876). It serves the current source after collecting static assets and restarting the verified runserver.

## Product and safety context

- GrowthTwin targets people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability reference, not first-release scope.
- Local product development with synthetic data is authorized. Keep Django 5.2/PostgreSQL modular monolith; use feature branches and PRs; do not push directly to `main`.
- The site demonstrates brief → plan/preview → deterministic editable copy → simulated pause → sample report. Anonymous session drafts are stored in PostgreSQL. No AI provider, ad account, publication, real spend, or real metrics are connected. Do not enter real or sensitive data.
- The Heroku `clearsessions` job's first run succeeded, but Scheduler is best-effort and its actual one-off dyno cost is unverified. It is not a real-data retention guarantee. Staging E2E, backup/restore, rollback, and final cost/CI recording remain gates before external beta or production.
- First advertiser workflow/destination, service packages/pricing, lead-delivery behavior, modality-specific production AI/tools/data terms, category-specific retention, and real-data admission remain undecided. The owner explicitly confirmed real-data use must wait until the system is fully ready. Do not connect accounts, accept real data, publish, spend, deploy production, or add paid services.

## Recent verified work

- Phase 1 acceptance was verified against the brief → preview → sample report journey. Manual desktop review at a 1252 px viewport found horizontal page overflow, a hard-to-read data-use notice, and a report action that could leave the report off-screen. PR #100 fixed all three; the refreshed desktop view had no horizontal scrollbar and the report was visible after navigation. Mobile remains covered by E2E.
- PR #96 corrected the first-visit data notice: inputs go to the GrowthTwin app and are stored as a temporary session draft; this prototype does not send them to AI services or ad platforms, publish, or spend.
- Two synthetic advertiser briefs and the existing-draft edit flow were reviewed. Plan/copy reflect supplied facts, and edited copy remains visibly stale until the advertiser chooses to regenerate it. No other defect was demonstrated.
- Local Workspace ownership tests passed 3/3 against a temporary in-memory SQLite test configuration. Local PostgreSQL test database creation remains blocked because the app role has `NOCREATEDB`; the configured role was not broadened. PR #102 and post-merge CI ran the full suite against PostgreSQL successfully.
- [ADR-0007](../adr/0007-workspace-ownership-and-retention.md) establishes a synthetic-only Phase 2 boundary: future campaign data is workspace-owned, anonymous drafts are not backfilled, and real-data retention must be defined by data category and purpose before launch. It is not legal approval to process personal data.
- PR #102 added the minimal `Workspace(owner, name, created_at)` model, user deletion cascade, migration, and owner-scoping tests. It is not yet used by signup or campaign UI. Django system check, migration consistency, Ruff lint/format, PR and post-merge CI passed.
- Review of `PROJECT.md`, `ROADMAP.md`, ADR-0004/0005/0007, and `AI_PROVIDERS.md` found strategic direction but no detailed first-release service blueprint. Platform, service packages, generated-lead routing, modality-specific AI tools, and real-data lifecycle remain open. ROADMAP now places that blueprint before further authenticated workspace UI or real-data use.

## Next action

Create and review the Phase 1.5 product/service blueprint: distinguish advertiser intake from ad-generated leads; define the first service and user journey; compare one destination's Türkiye API feasibility; map text/image/video AI evaluation; and specify user controls and data lifecycle. Keep all data synthetic while these decisions are open.
