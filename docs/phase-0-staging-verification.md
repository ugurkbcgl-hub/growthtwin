# Phase 0 staging verification readiness

Review date: 2026-10-01 22:19 +0300 (Europe/Istanbul)

The staging profile-edit E2E was run and passed against the approved staging app with a disposable least-privilege synthetic account and fabricated profile values. No restore, rollback, live account, campaign, spend, or new paid resource was used. Continue using synthetic values only.

## Verified baseline

- Current `main` baseline before this documentation update is `69476a62d2d289761d1aeef8c672e66dadc28b6d`, after PR #176. Its latest main CI run `36750735813` passed. No open PRs were listed at review time. The staging E2E below passed against this same commit, deployed as release v14.
- GitHub branch protection is enabled on `main`; the required context is `Django system check`, PR branches must be up to date, and admin enforcement is enabled.
- A direct GET to the approved staging `/health/` endpoint on 2026-09-30 returned HTTP 200 and `{"status":"ok","version":"unknown"}`. This verifies endpoint and database readiness, but the application response does not identify its code revision.
- The authenticated Heroku CLI release list showed the latest code deployment as v14, commit `69476a62`, on 2026-09-30; v11–v13 were configuration releases. The health endpoint returned HTTP 200 with `version: unknown`, so runtime revision reporting remains unresolved.
- The staging E2E runner exists at `apps/web/e2e/run_staging.py`, pinned to the approved HTTPS host. The passing staging check reused `e2e.profile_edit_flow.run_profile_edit_flow` through a one-time local helper; it verified login, profile save and persistence after reload, logout, and logged-out access protection. It used the disposable account `growthtwin-e2e-20260930`; no password was recorded.
- The approved resources remain one Basic dyno (~USD 0.010/hour), one Essential-0 Postgres (~USD 0.007/hour), and Standard Free Scheduler, with a previously observed estimate near USD 12/month. This is not an invoice; actual charges, tax, and Scheduler one-off dyno cost remain unverified. No resource was added in this work.

## Verification sequence and stop points

### 1. Staging browser E2E — passed for the profile-edit flow

Verified 2026-09-30 against release v14 (`69476a62`) on the approved HTTPS host. The account is a normal active user, not staff or superuser. It was used only with fabricated profile values. The account remains available for future staging checks; its password is not recorded in this repository or handoff.

The existing profile flow was invoked through a one-time local helper because staging-account setup required a password handoff. The standard runner remains available from `apps/web`: `python -m e2e.run_staging`.

Pass evidence: the browser flow completed login, saved the synthetic profile, verified persistence after reload, logged out, and confirmed protected profile access redirects to login. Browser context was closed; no state was persisted locally. This proves only the demo profile flow, not campaign authorization or publishing.

Before a future rerun, verify the deployed release and test target again. Stop if they differ, the disposable account is unavailable, any real data appears, or the result is ambiguous. The health endpoint still has `version: unknown` and cannot independently attest to the deployed revision.

### 2. Backup and restore — isolated fixture and local schema-only drills passed; data-bearing app restore remains unverified

The owner chose a local database rehearsal. On 2026-10-01, a temporary PostgreSQL 18.6 cluster bound only to `127.0.0.1` was initialized under the operating-system temporary directory. A fabricated marker row was captured with `pg_dump --format=custom`, restored with `pg_restore --no-owner --no-privileges` into a separate empty database, and verified. The temporary cluster, dump, and log were removed. No password was used, and no persistent local database or Heroku resource was changed.

This proves the local PostgreSQL dump/restore toolchain with a tiny synthetic fixture only. It does not verify the configured GrowthTwin development/test database, its data composition, its backup, or Heroku staging recovery. The authenticated Heroku CLI reported no staging backups, restores, or copies earlier on 2026-10-01; no remote capture/download/restore has been performed. Keep using a **new, uniquely named disposable local database** as the restore target. Never point a restore at the configured development/test database or staging, and never use `pg_restore --clean` against an existing database.

On 2026-10-01, the configured local `growthtwin` database was identified through a hidden password prompt. A custom-format **schema-only** dump restored to a newly created temporary database; the restored database had the same 11 public tables and every restored table was empty. No application records were included. This did not verify the source data composition, a full data-bearing application backup/restore, or Heroku staging recovery. The local Django test settings use in-memory SQLite; CI creates an ephemeral PostgreSQL service. There is no separately configured persistent PostgreSQL test database in the repository setup.

Next, create or otherwise identify an isolated local PostgreSQL rehearsal source populated only from Django migrations and explicitly fabricated test records. Take a custom-format dump and restore it into a newly created empty local database. Verify a known synthetic marker plus Django system and migration checks against the restored target. Keep the configured `growthtwin` development database and Heroku staging out of the restore path. Remove only the uniquely named disposable rehearsal source, restore target, and dump after validation. Do not expose database credentials in chat, logs, or command history. No new paid resource or Heroku data transfer is required.

Pass evidence so far: the isolated fixture row survived a local PostgreSQL 18.6 custom-format backup and restore, and the local app database schema-only restore matched 11 public tables with no rows. Full application-data restore remains unverified.

### 3. Deployment rollback — planning only; no deploy performed

First obtain a current release list and code revision from the authorized Heroku dashboard or an installed authenticated CLI. Select a known-good reviewed release, then check schema/migration compatibility before rollback. Never roll back across an irreversible migration without a tested recovery plan.

Pass evidence: restore the selected release through the approved deployment mechanism, verify health and deployed revision, run staging E2E, and record application/database recovery ordering. No rollback has been performed or verified; the health endpoint still cannot report the running revision.

### 4. Cost and CI gate — partially verified

The GitHub merge gate is verified above, and PR/post-merge CI results are recorded in the continuity state. The authenticated dashboard currently estimates about USD 12/month for the approved resources. This is not actual billed usage; tax treatment and Scheduler one-off dyno charges remain unverified. No resource was created for this check.

## Current blockers

- The health response still reports version `unknown`; runtime revision reporting is not wired or not populated.
- Backup/restore and rollback remain unverified and require a safe target/recovery procedure.

## Next action

Create an isolated PostgreSQL rehearsal source from migrations and fabricated records, then prove full custom-format dump/restore into a new empty local database and run Django checks there; do not use or overwrite configured `growthtwin` or staging.
