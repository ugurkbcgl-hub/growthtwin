# Phase 0 staging verification readiness

Review date: 2026-09-30 20:11 +0300 (Europe/Istanbul)

This review was read-only; no deployment, account creation, restore, rollback, paid resource, live account, campaign, or spend was performed. Use synthetic values only.

## Verified baseline

- Current `main` baseline after PR #174 is `05e102f26a5879d127914754128d1be08528c0db`. PR #171, #172 and #174 are merged; PR #171 required CI `36745452282` and post-merge CI `36745746001` passed; PR #172 required CI `36746196220` and post-merge CI `36746483602` passed; PR #174 required CI `36748631258` and post-merge CI `36748897583` passed. All listed runs included Django tests and browser E2E.
- GitHub branch protection is enabled on `main`; the required context is `Django system check`, PR branches must be up to date, and admin enforcement is enabled.
- A direct GET to the approved staging `/health/` endpoint on 2026-09-30 returned HTTP 200 and `{"status":"ok","version":"unknown"}`. This verifies endpoint and database readiness, but the application response does not identify its code revision.
- The authenticated Heroku overview/activity feed showed one Basic web dyno and the latest code deployment as release v5, commit `ac2f627d`, dated 2026-09-27. Later releases v6–v10 shown in the feed changed configuration; no later code deployment was listed. The deployed code revision is therefore known from the dashboard snapshot, though the runtime health endpoint still reports `unknown`.
- The staging E2E runner exists at `apps/web/e2e/run_staging.py`. It is pinned to the approved HTTPS host, prompts locally for a disposable account username/password, runs the profile-edit flow, and suppresses details for unexpected failures. No staging E2E was run in this review.
- Heroku CLI is not installed, but the authenticated dashboard was reviewed read-only on 2026-09-30. It showed one Basic dyno (~USD 0.010/hour), one Essential-0 Postgres (~USD 0.007/hour), Standard Free Scheduler, and an estimated total of about USD 12/month. The dashboard estimate is not an invoice; actual charges, tax, and Scheduler one-off dyno cost remain unverified.

## Verification sequence and stop points

### 1. Staging browser E2E — ready after test-account setup

Prerequisite: create or identify a dedicated disposable account on the approved staging app through its authorized admin path. Use fabricated profile details only. Do not place a password in chat, Git, or logs; enter it only at the runner's hidden local prompt.

Run from `apps/web` after confirming Python dependencies and Chromium are available: `python -m e2e.run_staging`.

Pass evidence: runner exits successfully, confirms profile save and persistence after reload, confirms logout blocks the protected profile, and reports no saved browser state. Record timestamp, deployed revision if known, and outcome only. Do not treat this profile flow as evidence for campaign authorization/publishing.

Stop if the deployed revision cannot be matched to the reviewed code, the disposable account is unavailable, any real data appears, or the result is ambiguous. The dashboard lists `ac2f627d`, while the current health response still has `version: unknown`; verify that the existing app release and the intended test target match before running.

### 2. Backup and restore — planning only; not safe to execute yet

Before a restore attempt, verify the exact database plan's included backup/restore capability and current recovery behavior. Define a synthetic-only snapshot, recovery point, expected data, and post-restore checks. Preserve the original snapshot and record the recovery order.

Do not restore over the only staging database during this readiness pass: restore can overwrite existing data, and the account's test-data state is not established. Do not add a second database or backup add-on without a new cost/owner decision. A future rehearsal needs a documented non-destructive target or an explicitly approved maintenance window and recovery plan.

Pass evidence: identify the snapshot/recovery point, restore target and duration; verify expected synthetic records and Django health; record the result and cleanup. No backup/restore has been performed or verified.

### 3. Deployment rollback — planning only; no deploy performed

First obtain a current release list and code revision from the authorized Heroku dashboard or an installed authenticated CLI. Select a known-good reviewed release, then check schema/migration compatibility before rollback. Never roll back across an irreversible migration without a tested recovery plan.

Pass evidence: restore the selected release through the approved deployment mechanism, verify health and deployed revision, run staging E2E, and record application/database recovery ordering. No rollback has been performed or verified; current deployment revision remains unknown.

### 4. Cost and CI gate — partially verified

The GitHub merge gate is verified above, and PR/post-merge CI results are recorded in the continuity state. The authenticated dashboard currently estimates about USD 12/month for the approved resources. This is not actual billed usage; tax treatment and Scheduler one-off dyno charges remain unverified. No resource was created for this check.

## Current blockers

- The dashboard identifies deployed code as `ac2f627d` (last code deploy shown 2026-09-27), but the health response still reports version `unknown`; runtime revision reporting is not wired or not populated.
- No disposable staging account is provisioned/verified for the browser E2E.
- Backup/restore and rollback remain unverified and require a safe target/recovery procedure.

## Next action

Provision a disposable synthetic staging account through the authorized admin path, then run the existing `python -m e2e.run_staging` flow with credentials entered only at its hidden local prompts. The Heroku dashboard lists `ac2f627d`, but the runtime version is unknown; confirm the test target matches that reviewed release before running the E2E.
