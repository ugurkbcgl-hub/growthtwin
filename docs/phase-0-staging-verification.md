# Phase 0 staging verification readiness

Review date: 2026-10-03 12:09 +0300 (Europe/Istanbul)

The staging profile-edit E2E was run and passed against the approved staging app with a disposable least-privilege synthetic account and fabricated profile values. No restore, rollback, live account, campaign, spend, or new paid resource was used. Continue using synthetic values only.

## Verified baseline

- Historical baseline for the 2026-10-01 verification: `main` was `69476a62d2d289761d1aeef8c672e66dadc28b6d` after PR #176, and the staging E2E below passed against that commit as release v14.
- Current CLI recheck on 2026-10-03: the latest Heroku release is v16, deployed from `8e29944e024554098bd1c0a90e4b7b799362370a` and succeeded. At deployment time, repository `main` was that commit after PR #212; required CI `37111641208` and post-merge CI `37111781360` passed. A subsequent documentation-only commit records the verified result.
- GitHub branch protection is enabled on `main`; the required context is `Django system check`, PR branches must be up to date, and admin enforcement is enabled.
- A direct GET to the approved staging `/health/` endpoint on 2026-09-30 returned HTTP 200 and `{"status":"ok","version":"unknown"}`. This verifies endpoint and database readiness, but the application response does not identify its code revision.
- The earlier 11:01 +0300 staging health check still reflected release v14 (`69476a62`) and returned `version: unknown`. Subsequent Heroku CLI release checks observed v15 and then v16.
- PR #206 updates health revision lookup to prefer `HEROKU_BUILD_COMMIT`, then legacy `HEROKU_SLUG_COMMIT`; it is deployed. Heroku's official [Dyno Metadata documentation](https://devcenter.heroku.com/articles/dyno-metadata) requires both `runtime-dyno-metadata` and the additional `runtime-dyno-build-metadata` flag for `HEROKU_BUILD_COMMIT`. Both were enabled before v16. The v16 health response reports `8e29944e024554098bd1c0a90e4b7b799362370a`, matching `main`; config-var values were not revealed. The release command reported no migrations to apply.
- The staging E2E runner exists at `apps/web/e2e/run_staging.py`, pinned to the approved HTTPS host. The passing staging check reused `e2e.profile_edit_flow.run_profile_edit_flow` through a one-time local helper; it verified login, profile save and persistence after reload, logout, and logged-out access protection. It used the disposable account `growthtwin-e2e-20260930`; no password was recorded.
- The approved resources remain one Basic dyno (~USD 0.010/hour), one Essential-0 Postgres (~USD 0.007/hour), and Standard Free Scheduler, with a previously observed estimate near USD 12/month. This is not an invoice; actual charges, tax, and Scheduler one-off dyno cost remain unverified. No resource was added in this work.

## Verification sequence and stop points

### 1. Staging browser E2E — passed for the profile-edit flow

Verified 2026-09-30 against release v14 (`69476a62`) on the approved HTTPS host. The account is a normal active user, not staff or superuser. It was used only with fabricated profile values. The account remains available for future staging checks; its password is not recorded in this repository or handoff.

The existing profile flow was invoked through a one-time local helper because staging-account setup required a password handoff. The standard runner remains available from `apps/web`: `python -m e2e.run_staging`.

Pass evidence: the browser flow completed login, saved the synthetic profile, verified persistence after reload, logged out, and confirmed protected profile access redirects to login. Browser context was closed; no state was persisted locally. This proves only the demo profile flow, not campaign authorization or publishing.

Before a future rerun, verify the deployed release and test target again. Stop if they differ, the disposable account is unavailable, any real data appears, or the result is ambiguous. The current health endpoint now identifies the v16 revision.

### 2. Backup and restore — isolated synthetic app drill passed; configured DB and staging recovery remain unverified

The owner chose a local database rehearsal. On 2026-10-01, a temporary PostgreSQL 18.6 cluster bound only to `127.0.0.1` was initialized under the operating-system temporary directory. A fabricated marker row was captured with `pg_dump --format=custom`, restored with `pg_restore --no-owner --no-privileges` into a separate empty database, and verified. The temporary cluster, dump, and log were removed. No password was used, and no persistent local database or Heroku resource was changed.

This proves the local PostgreSQL dump/restore toolchain with a tiny synthetic fixture only. It does not verify the configured GrowthTwin development/test database, its data composition, its backup, or Heroku staging recovery. The authenticated Heroku CLI reported no staging backups, restores, or copies earlier on 2026-10-01; no remote capture/download/restore has been performed. Keep using a **new, uniquely named disposable local database** as the restore target. Never point a restore at the configured development/test database or staging, and never use `pg_restore --clean` against an existing database.

On 2026-10-01, the configured local `growthtwin` database was identified through a hidden password prompt. A custom-format **schema-only** dump restored to a newly created temporary database; the restored database had the same 11 public tables and every restored table was empty. No application records were included. This did not verify the source data composition, a full data-bearing application backup/restore, or Heroku staging recovery. The local Django test settings use in-memory SQLite; CI creates an ephemeral PostgreSQL service. There is no separately configured persistent PostgreSQL test database in the repository setup.

On 2026-10-01, an additional temporary PostgreSQL 18.6 cluster bound to loopback was initialized. Django migrations were applied to a new source database, one fabricated auth account with an unusable password was added, and a full custom-format dump was restored into a separate empty database. The synthetic marker was found exactly once; `manage.py check --database default` and `manage.py migrate --check --noinput` both passed on the restored target. The server was stopped. No configured local `growthtwin` or Heroku database was used. The cluster directory and dump remain under `%TEMP%` at `gwt_full_rehearsal_a656127cec`; cleanup was attempted only after confirming the exact resolved path, but the command tool's automatic policy blocked the recursive removal. Its contents are synthetic rehearsal data only.

This verifies a Django-shaped, data-bearing local round-trip, not a backup of the configured `growthtwin` database or Heroku staging. Clear the stopped temporary rehearsal directory before continuing to rollback planning.

### 3. Deployment rollback — planning only; no deploy performed

First obtain a current release list and code revision from the authorized Heroku dashboard or an installed authenticated CLI. Select a known-good reviewed release, then check schema/migration compatibility before rollback. Never roll back across an irreversible migration without a tested recovery plan.

Pass evidence: restore the selected release through the approved deployment mechanism, verify health and deployed revision, run staging E2E, and record application/database recovery ordering. No rollback has been performed or verified; the health endpoint still cannot report the running revision.

### 4. Cost and CI gate — partially verified

The GitHub merge gate is verified above, and PR/post-merge CI results are recorded in the continuity state. The authenticated dashboard currently estimates about USD 12/month for the approved resources. This is not actual billed usage; tax treatment and Scheduler one-off dyno charges remain unverified. No resource was created for this check.

## Current blockers

- After v16, staging `/health/` returned HTTP 200 with a revision matching current `main`. The pinned profile-edit E2E has not been rerun on v16; backup/restore and rollback remain unverified.
- Backup/restore and rollback remain unverified and require a safe target/recovery procedure.

## Next action

Rerun the pinned profile-edit E2E against v16 with the existing disposable synthetic account; enter its password only at the hidden local terminal prompt and do not record it. Then keep backup/restore and rollback as separate Phase 0 gates. Do not expose config-var values or use real data.
