# Phase 0 staging verification readiness

Review date: 2026-09-30 20:00 +0300 (Europe/Istanbul)

This review was read-only; no deployment, account creation, restore, rollback, paid resource, live account, campaign, or spend was performed. Use synthetic values only.

## Verified baseline

- Current `main` after PR #172 is `5d63290b44503992473a2c9469d3733e04a6f0ab`. PR #171 and #172 are merged; PR #171 required CI `36745452282` and post-merge CI `36745746001` passed; PR #172 required CI `36746196220` and post-merge CI `36746483602` passed. Both runs included Django tests and browser E2E.
- GitHub branch protection is enabled on `main`; the required context is `Django system check`, PR branches must be up to date, and admin enforcement is enabled.
- A direct GET to the approved staging `/health/` endpoint on 2026-09-30 returned HTTP 200 and `{"status":"ok","version":"unknown"}`. This verifies endpoint and database readiness at that time, not the deployed revision.
- The staging E2E runner exists at `apps/web/e2e/run_staging.py`. It is pinned to the approved HTTPS host, prompts locally for a disposable account username/password, runs the profile-edit flow, and suppresses details for unexpected failures. No staging E2E was run in this review.
- Heroku CLI is not installed in this workspace. The dashboard's current release, resource and cost details therefore were not rechecked. `DEPLOYMENT.md` retains older observations and labels them with their observation dates.

## Verification sequence and stop points

### 1. Staging browser E2E — ready after test-account setup

Prerequisite: create or identify a dedicated disposable account on the approved staging app through its authorized admin path. Use fabricated profile details only. Do not place a password in chat, Git, or logs; enter it only at the runner's hidden local prompt.

Run from `apps/web` after confirming Python dependencies and Chromium are available: `python -m e2e.run_staging`.

Pass evidence: runner exits successfully, confirms profile save and persistence after reload, confirms logout blocks the protected profile, and reports no saved browser state. Record timestamp, deployed revision if known, and outcome only. Do not treat this profile flow as evidence for campaign authorization/publishing.

Stop if the deployed revision is unknown, the disposable account is unavailable, any real data appears, or the result is ambiguous. The current health response has `version: unknown`.

### 2. Backup and restore — planning only; not safe to execute yet

Before a restore attempt, verify the exact database plan's included backup/restore capability and current recovery behavior. Define a synthetic-only snapshot, recovery point, expected data, and post-restore checks. Preserve the original snapshot and record the recovery order.

Do not restore over the only staging database during this readiness pass: restore can overwrite existing data, and the account's test-data state is not established. Do not add a second database or backup add-on without a new cost/owner decision. A future rehearsal needs a documented non-destructive target or an explicitly approved maintenance window and recovery plan.

Pass evidence: identify the snapshot/recovery point, restore target and duration; verify expected synthetic records and Django health; record the result and cleanup. No backup/restore has been performed or verified.

### 3. Deployment rollback — planning only; no deploy performed

First obtain a current release list and code revision from the authorized Heroku dashboard or an installed authenticated CLI. Select a known-good reviewed release, then check schema/migration compatibility before rollback. Never roll back across an irreversible migration without a tested recovery plan.

Pass evidence: restore the selected release through the approved deployment mechanism, verify health and deployed revision, run staging E2E, and record application/database recovery ordering. No rollback has been performed or verified; current deployment revision remains unknown.

### 4. Cost and CI gate — partially verified

The GitHub merge gate is verified above, and PR/post-merge CI results are recorded in the continuity state. Current Heroku invoice/resource usage and Scheduler one-off cost are not verified by this review because Heroku CLI is unavailable and the prior dashboard observations are dated. Refresh those values from the authenticated dashboard before any further staging change. Do not create resources for this check.

## Current blockers

- Deployed revision is unknown from the public health response.
- No disposable staging account is provisioned/verified for the browser E2E.
- No authenticated Heroku dashboard session was used from this workspace; live release and current billing could not be checked.
- Backup/restore and rollback remain unverified and require a safe target/recovery procedure.

## Next action

Provision a disposable synthetic staging account through the authorized admin path, then run the existing `python -m e2e.run_staging` flow with credentials entered only at its hidden local prompts. Before doing so, confirm the staging revision through the authenticated Heroku dashboard; if it remains unknown, resolve that deployment-identification gap first.
