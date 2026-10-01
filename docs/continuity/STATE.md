# GrowthTwin — current handoff

Last verified: 2026-10-01 23:24 +0300 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Clean `main` is at `b9fc8becb05f853f6d0929d483b540454bf4d41b` after PR #183. PR CI `36916705107` and post-merge main CI `36916997082` passed. No open PRs are listed. `main` branch protection is enabled with required check `Django system check`, up-to-date PR branches, and admin enforcement.
- This status refresh is being delivered through a feature branch/PR. Recheck live branch, worktree, open PRs, and CI before future actions. Do not push directly to `main`.
- Heroku staging release v14 deploys `69476a62` (2026-09-30). `/health/` returned HTTP 200 with `version: unknown`; runtime revision reporting remains unresolved. Releases v11–v13 updated database and Django secret configuration; secret values are not recorded here.
- On 2026-10-01, the signed-in Heroku dashboard showed staging release v14 running commit `69476a62`; its release log applied the current `workspaces`, `campaigns`, and `site` migrations. The Essential-0 PostgreSQL 18.4 add-on was Available at 8.74 MB of 1 GB and 0 of 20 connections. The dashboard reports database `ROLLBACK Unsupported` and `MAINTENANCE Unsupported`. No Heroku action was taken.
- The Heroku release history shows v13 was a configuration-only release after v5, the most recent earlier code deployment (`ac2f627d`). Rolling the app code back to v5 would leave the v14 database and its newer migrations in place; compatibility has not been proven. Do not roll back the app or database until a reviewed recovery procedure and a compatible target are established. Heroku's app-release rollback does not revert add-on data; database rollback is unavailable on this plan.
- Existing approved staging resources remain the Basic web dyno, Essential-0 PostgreSQL, and Standard Free Scheduler. Previously observed estimate is about USD 12/month before tax; actual billing and one-off Scheduler dyno cost remain unverified. No resource was added.

## Completed

- Created and verified a disposable, active staging user `growthtwin-e2e-20260930` with normal user permissions (`staff=False`, `superuser=False`). Its synthetic profile is `GrowthTwin E2E Sentetik Klinik`, `Test Şehri`, `0000000000`, and `https://example.invalid`.
- Against staging release v14, the profile-edit browser flow passed: unauthenticated redirect, login, synthetic profile save, persistence after reload, logout, and protected-route check after logout. It reused `e2e.profile_edit_flow.run_profile_edit_flow` through a one-time local helper. The password is not stored in Git, docs, logs, or this handoff; the owner manages it.
- PR #177 updated PROJECT, ROADMAP, and the Phase 0 staging verification sequence; it passed required and post-merge CI. At that point, no backup/restore or rollback had been performed.
- PR #181 recorded the local app schema-only rehearsal and clarified that local Django tests use in-memory SQLite; required CI `36913776174` and post-merge CI `36914064357` passed.
- PR #182 refreshed the preceding snapshot; required CI `36914398066` and post-merge CI `36915120461` passed.
- On 2026-10-01, the authenticated Heroku CLI reported no staging backups, restores, or copies. The staging database remains untouched. Heroku documents optional daily PGBackups for Essential plans (7 daily/1 weekly retention), no Essential fork/rollback, restore as full target replacement, and US storage for logical dumps. A Heroku capture/download is not part of the owner's selected local rehearsal.
- On 2026-10-01, an isolated temporary PostgreSQL 18.6 cluster bound to loopback passed a synthetic custom-format dump/restore round-trip into a separate empty database. The synthetic marker was verified and temporary cluster/dump/log were removed. This does not verify the configured GrowthTwin test DB or staging recovery. No persistent database, Heroku data, paid resource, or credential was touched.
- On 2026-10-01, the local `growthtwin` database passed a schema-only custom-format dump/restore into a new empty temporary database: 11 public tables matched and the restored tables contained no rows. This did not include or inspect application records and did not establish that source records are synthetic. The local project test settings use in-memory SQLite; CI uses an ephemeral PostgreSQL service. No persistent database or Heroku resource was changed.
- On 2026-10-01, an isolated temporary PostgreSQL 18.6 cluster was migrated with Django, seeded with one fabricated auth account that has no usable password, then custom-format dumped and restored into a new empty database. The marker was present exactly once; Django system and migration checks passed on the restored target. The server stopped successfully. The local source DB and Heroku were untouched. Cleanup of `%TEMP%\gwt_full_rehearsal_a656127cec` was rejected by the command policy, so synthetic-only dump/cluster files remain until removed through an allowed file operation.
- The temp rehearsal directory removal was attempted again on 2026-10-01 and blocked by command policy. The temporary database server is stopped; the folder contains only synthetic rehearsal residue. No alternate deletion method was used.

## Open blockers and limits

- The isolated synthetic app-data restore and local `growthtwin` schema-only restore are verified, but backup/restore of the configured database and controlled staging rollback remain unverified. The stopped temporary synthetic rehearsal folder still needs cleanup through an allowed file operation. Never overwrite the configured source database or staging.
- The staging health endpoint does not identify its code revision. Verify Heroku release and target again before future staging checks.
- Actual charges, taxes, and Scheduler one-off cost remain unverified. Keep hosted data synthetic; no live advertiser account, campaign publication, or ad spend is enabled.

## Next action

Have the stopped synthetic-only folder `%TEMP%\gwt_full_rehearsal_a656127cec` removed through an allowed local file operation; recursive removal is blocked by the current command policy. Do not touch configured `growthtwin` or staging data. After cleanup, prepare a reviewed staging rollback/recovery rehearsal that accounts for the v14 schema and the Essential-0 database's lack of rollback support; do not execute a rollback or provision a backup resource.
