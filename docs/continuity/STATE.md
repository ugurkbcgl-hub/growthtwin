# GrowthTwin — current handoff

Last verified: 2026-10-01 22:26 +0300 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Clean `main` is at `9b259eeae4dfd18dfa034509e3a466e7e274f988` after PR #181. PR CI `36913776174` and post-merge main CI `36914064357` passed. No open PRs were listed at verification. `main` branch protection is enabled with required check `Django system check`, up-to-date PR branches, and admin enforcement.
- This state refresh records the just-merged documentation PR; recheck live branch, worktree, open PRs, and CI before future actions. Do not push directly to `main`.
- Heroku staging release v14 deploys `69476a62` (2026-09-30). `/health/` returned HTTP 200 with `version: unknown`; runtime revision reporting remains unresolved. Releases v11–v13 updated database and Django secret configuration; secret values are not recorded here.
- Existing approved staging resources remain the Basic web dyno, Essential-0 PostgreSQL, and Standard Free Scheduler. Previously observed estimate is about USD 12/month before tax; actual billing and one-off Scheduler dyno cost remain unverified. No resource was added.

## Completed

- Created and verified a disposable, active staging user `growthtwin-e2e-20260930` with normal user permissions (`staff=False`, `superuser=False`). Its synthetic profile is `GrowthTwin E2E Sentetik Klinik`, `Test Şehri`, `0000000000`, and `https://example.invalid`.
- Against staging release v14, the profile-edit browser flow passed: unauthenticated redirect, login, synthetic profile save, persistence after reload, logout, and protected-route check after logout. It reused `e2e.profile_edit_flow.run_profile_edit_flow` through a one-time local helper. The password is not stored in Git, docs, logs, or this handoff; the owner manages it.
- PR #177 updated PROJECT, ROADMAP, and the Phase 0 staging verification sequence; it passed required and post-merge CI. At that point, no backup/restore or rollback had been performed.
- PR #181 recorded the local app schema-only rehearsal and clarified that local Django tests use in-memory SQLite; required CI `36913776174` and post-merge CI `36914064357` passed.
- On 2026-10-01, the authenticated Heroku CLI reported no staging backups, restores, or copies. The staging database remains untouched. Heroku documents optional daily PGBackups for Essential plans (7 daily/1 weekly retention), no Essential fork/rollback, restore as full target replacement, and US storage for logical dumps. A Heroku capture/download is not part of the owner's selected local rehearsal.
- On 2026-10-01, an isolated temporary PostgreSQL 18.6 cluster bound to loopback passed a synthetic custom-format dump/restore round-trip into a separate empty database. The synthetic marker was verified and temporary cluster/dump/log were removed. This does not verify the configured GrowthTwin test DB or staging recovery. No persistent database, Heroku data, paid resource, or credential was touched.
- On 2026-10-01, the local `growthtwin` database passed a schema-only custom-format dump/restore into a new empty temporary database: 11 public tables matched and the restored tables contained no rows. This did not include or inspect application records and did not establish that source records are synthetic. The local project test settings use in-memory SQLite; CI uses an ephemeral PostgreSQL service. No persistent database or Heroku resource was changed.

## Open blockers and limits

- The local PostgreSQL toolchain and local `growthtwin` schema-only restore are verified, but a full application-data restore and controlled staging rollback remain unverified. Never overwrite the configured source database or staging.
- The staging health endpoint does not identify its code revision. Verify Heroku release and target again before future staging checks.
- Actual charges, taxes, and Scheduler one-off cost remain unverified. Keep hosted data synthetic; no live advertiser account, campaign publication, or ad spend is enabled.

## Next action

Create an isolated PostgreSQL rehearsal source from Django migrations and explicitly fabricated records, restore its full custom-format dump into a new empty local database, and verify the synthetic marker plus Django checks without touching configured `growthtwin` or staging.
