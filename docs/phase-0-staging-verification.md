# Phase 0 staging verification readiness

Review date: 2026-10-03 13:22 +0300 (Europe/Istanbul)

The staging profile-edit E2E passed against the approved staging app's v16 release, was repeated on v15 during a controlled release rollback on 2026-10-03, and passed again after returning to v16. A disposable least-privilege synthetic account and fabricated profile values were used. The temporary account password was reset and not recorded. No live account, campaign, spend, or new paid resource was used. Continue using synthetic values only.

## Verified baseline

- Historical baseline for the 2026-10-01 verification: `main` was `69476a62d2d289761d1aeef8c672e66dadc28b6d` after PR #176, and the staging E2E below passed against that commit as release v14.
- Current CLI recheck on 2026-10-03: the latest Heroku release is v16, deployed from `8e29944e024554098bd1c0a90e4b7b799362370a` and succeeded. At deployment time, repository `main` was that commit after PR #212; required CI `37111641208` and post-merge CI `37111781360` passed. A subsequent documentation-only commit records the verified result.
- GitHub branch protection is enabled on `main`; the required context is `Django system check`, PR branches must be up to date, and admin enforcement is enabled.
- A direct GET to the approved staging `/health/` endpoint on 2026-09-30 returned HTTP 200 and `{"status":"ok","version":"unknown"}`. This verifies endpoint and database readiness, but the application response does not identify its code revision.
- The earlier 11:01 +0300 staging health check still reflected release v14 (`69476a62`) and returned `version: unknown`. Subsequent Heroku CLI release checks observed v15 and then v16.
- PR #206 updates health revision lookup to prefer `HEROKU_BUILD_COMMIT`, then legacy `HEROKU_SLUG_COMMIT`; it is deployed. Heroku's official [Dyno Metadata documentation](https://devcenter.heroku.com/articles/dyno-metadata) requires both `runtime-dyno-metadata` and the additional `runtime-dyno-build-metadata` flag for `HEROKU_BUILD_COMMIT`. Both were enabled before v16. The v16 health response reports `8e29944e024554098bd1c0a90e4b7b799362370a`, matching `main`; config-var values were not revealed. The release command reported no migrations to apply.
- The staging E2E runner exists at `apps/web/e2e/run_staging.py`, pinned to the approved HTTPS host. The passing staging check reused `e2e.profile_edit_flow.run_profile_edit_flow` through a one-time local helper; it verified login, profile save and persistence after reload, logout, and logged-out access protection. It used the disposable account `growthtwin-e2e-20260930`; no password was recorded.
- The approved resources remain one Basic dyno (~USD 0.010/hour), one Essential-0 Postgres (~USD 0.007/hour), and Standard Free Scheduler, with a previously observed estimate near USD 12/month. On 2026-10-03, Heroku billing displayed $0.00 current usage and the September invoice at $1.37 Pending. This is not a finalized usage total; tax and Scheduler one-off dyno costs remain unverified. No resource was added in this work.

## Verification sequence and stop points

### 1. Staging browser E2E — passed for the profile-edit flow on v14 and v16

Initially verified 2026-09-30 against release v14 (`69476a62`), then rerun 2026-10-03 against release v16 (`8e29944`) on the approved HTTPS host. The account is a normal active user, not staff or superuser. It was used only with fabricated profile values. Before the rerun, its password was reset through Django's `changepassword` management command on the existing Heroku app; the password is not recorded in this repository or handoff.

The standard runner at `apps/web/e2e/run_staging.py` completed successfully with `python -m e2e.run_staging`.

Pass evidence: the browser flow completed login, saved the synthetic profile, verified persistence after reload, logged out, and confirmed protected profile access redirects to login. Browser context was closed; no state was persisted locally. This proves only the demo profile flow, not campaign authorization or publishing.

Before a future rerun, verify the deployed release and test target again. Stop if they differ, the disposable account is unavailable, any real data appears, or the result is ambiguous. The current health endpoint now identifies the v16 revision.

### 2. Backup and restore — isolated synthetic app drill passed; configured DB and staging recovery remain unverified

The owner chose a local database rehearsal. On 2026-10-01, a temporary PostgreSQL 18.6 cluster bound only to `127.0.0.1` was initialized under the operating-system temporary directory. A fabricated marker row was captured with `pg_dump --format=custom`, restored with `pg_restore --no-owner --no-privileges` into a separate empty database, and verified. The temporary cluster, dump, and log were removed. No password was used, and no persistent local database or Heroku resource was changed.

This proves the local PostgreSQL dump/restore toolchain with a tiny synthetic fixture only. It does not verify the configured GrowthTwin development/test database, its data composition, its backup, or Heroku staging recovery. The authenticated Heroku CLI reported no staging backups, restores, or copies earlier on 2026-10-01; no remote capture/download/restore has been performed. Keep using a **new, uniquely named disposable local database** as the restore target. Never point a restore at the configured development/test database or staging, and never use `pg_restore --clean` against an existing database.

On 2026-10-01, the configured local `growthtwin` database was identified through a hidden password prompt. A custom-format **schema-only** dump restored to a newly created temporary database; the restored database had the same 11 public tables and every restored table was empty. No application records were included. This did not verify the source data composition, a full data-bearing application backup/restore, or Heroku staging recovery. The local Django test settings use in-memory SQLite; CI creates an ephemeral PostgreSQL service. There is no separately configured persistent PostgreSQL test database in the repository setup.

On 2026-10-01, an additional temporary PostgreSQL 18.6 cluster bound to loopback was initialized. Django migrations were applied to a new source database, one fabricated auth account with an unusable password was added, and a full custom-format dump was restored into a separate empty database. The synthetic marker was found exactly once; `manage.py check --database default` and `manage.py migrate --check --noinput` both passed on the restored target. The server was stopped. No configured local `growthtwin` or Heroku database was used. The cluster directory and dump remain under `%TEMP%` at `gwt_full_rehearsal_a656127cec`; cleanup was attempted only after confirming the exact resolved path, but the command tool's automatic policy blocked the recursive removal. Its contents are synthetic rehearsal data only.

This verifies a Django-shaped, data-bearing local round-trip, not a backup of the configured `growthtwin` database or Heroku staging. The stopped temporary rehearsal directory remains because a recursive cleanup request was blocked by tool policy; it is not the source or target for any subsequent restore.

### 3. Deployment rollback — verified between same-code releases

On 2026-10-03, v16 (`8e29944`) was rolled back to v15 (`c13ba96`), creating v17. Heroku reported no migrations to apply. `/health/` returned HTTP 200 and revision `c13ba96ae610778ad9a924919a7bfabb71f0b12a`; the profile-edit E2E passed on v15. The app was then rolled back to v16, creating v18; Heroku again reported no migrations. `/health/` returned HTTP 200 and revision `8e29944e024554098bd1c0a90e4b7b799362370a`, and the profile-edit E2E passed again. Git confirms v15/v16 differ only in documentation, with no application code or migration changes. This verifies the Heroku release rollback mechanism for same-code releases and confirms v16 was restored. It does not prove recovery across an app-code or schema change, and Heroku rollback does not restore database contents.

Pass evidence: both rollback releases were created successfully, matching health revisions were checked, no migrations ran, and synthetic profile E2E passed on both versions. No add-on was provisioned or removed.

### 4. Cost and CI gate — partially verified

The GitHub merge gate is verified above, and PR/post-merge CI results are recorded in the continuity state. The authenticated billing page displayed $0.00 current usage and a September invoice of $1.37 Pending. This is not a finalized total; tax treatment and Scheduler one-off dyno charges remain unverified. No resource was created for this check.

## Current blockers

- Configured local database and Heroku database backup/restore remain unverified. The configured local database's data composition has not been established; do not dump or restore it until synthetic-only content is verified.
- A read-only inventory of the configured local `growthtwin` database ran via `scripts/dev.ps1`, with no `DATABASE_URL` override and the helper's loopback PostgreSQL settings. Aggregate results: 1 account with a test-marked username and an email that is blank or in a reserved example domain; 0 demo profiles; 8 anonymous campaign drafts not matching the current fixed synthetic sample; 9 sessions; and 1 workspace campaign whose base matched the fixed sample but which has creative versions. No username, email, or content value was printed. The old drafts and creative versions remain unclassified; no full data-bearing dump or restore was attempted.
- The stopped synthetic PostgreSQL rehearsal directory remains at `%TEMP%\gwt_full_rehearsal_a656127cec`. Its exact direct-child path, non-reparse-point status, contents, and absence of a PostgreSQL process using that directory were checked. Recursive cleanup was blocked by tool policy; it was left untouched and no alternate deletion method was attempted.
- Rollback was verified only between v15 and v16, whose application code is identical. Recovery across app-code, config-var, schema, or database-state changes remains unverified.
- Final Heroku usage, tax, and Scheduler one-off costs remain unverified.

## Next action

Keep full backup/restore of the configured local database deferred while legacy drafts and workspace creative values remain unclassified. Leave this database untouched. For the current handoff scope, do not begin product features until Phase 0 is complete. The next action is to obtain privacy-preserving, owner-approved evidence that the unclassified legacy drafts and workspace creative values are synthetic; do not inspect or export their contents to establish this. Do not retry recursive deletion through an alternate tool after the cleanup request was blocked. Do not expose config-var values or use real data.
