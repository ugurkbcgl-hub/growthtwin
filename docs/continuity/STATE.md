# GrowthTwin — current handoff

Last verified: 2026-10-02 00:55 +0300 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Clean `main` is at `1e16ac2e4e7e2c72077bdd76d0632a5bde1fb185` after PR #187. PR #187 CI `36930844437` and post-merge main CI `36931124672` passed, including Django tests and browser E2E. No open PRs were listed after merge. `main` branch protection requires `Django system check`, up-to-date PR branches, and admin enforcement.
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
- PR #184 recorded verified staging rollback limits; required CI `36921487830` and post-merge main CI `36924472563` passed.
- PR #185 added owner-scoped editing of synthetic creative variants, appended version history, bounded fields and synthetic-only confirmation. CI `36927616136` passed on rerun after the initial run stalled during Chromium setup; post-merge main CI `36928662971` passed. No local tests were run for this slice.
- PR #187 added browser E2E coverage for editing a creative, requiring synthetic confirmation, saving an appended version, reading the old version, and checking narrow/desktop layouts for overflow. Focused local Playwright E2E passed against in-memory SQLite; required CI `36930844437` and post-merge main CI `36931124672` passed. No Heroku or real advertiser data was used.
- On 2026-10-01, the authenticated Heroku CLI reported no staging backups, restores, or copies. The staging database remains untouched. Heroku documents optional daily PGBackups for Essential plans (7 daily/1 weekly retention), no Essential fork/rollback, restore as full target replacement, and US storage for logical dumps. A Heroku capture/download is not part of the owner's selected local rehearsal.
- On 2026-10-01, an isolated temporary PostgreSQL 18.6 cluster bound to loopback passed a synthetic custom-format dump/restore round-trip into a separate empty database. The synthetic marker was verified and temporary cluster/dump/log were removed. This does not verify the configured GrowthTwin test DB or staging recovery. No persistent database, Heroku data, paid resource, or credential was touched.
- On 2026-10-01, the local `growthtwin` database passed a schema-only custom-format dump/restore into a new empty temporary database: 11 public tables matched and the restored tables contained no rows. This did not include or inspect application records and did not establish that source records are synthetic. The local project test settings use in-memory SQLite; CI uses an ephemeral PostgreSQL service. No persistent database or Heroku resource was changed.
- On 2026-10-01, an isolated temporary PostgreSQL 18.6 cluster was migrated with Django, seeded with one fabricated auth account that has no usable password, then custom-format dumped and restored into a new empty database. The marker was present exactly once; Django system and migration checks passed on the restored target. The server stopped successfully. The local source DB and Heroku were untouched. Cleanup of `%TEMP%\gwt_full_rehearsal_a656127cec` was rejected by the command policy, so synthetic-only dump/cluster files remain until removed through an allowed file operation.
- The temp rehearsal directory removal was attempted again on 2026-10-02 and blocked by command policy. The temporary database server is stopped; the folder contains only synthetic rehearsal residue. No alternate deletion method was used.

## Open blockers and limits

- The isolated synthetic app-data restore and local `growthtwin` schema-only restore are verified, but backup/restore of the configured database and controlled staging rollback remain unverified. The stopped temporary synthetic rehearsal folder still needs cleanup through an allowed file operation. This does not block local synthetic-data product work. Never overwrite the configured source database or staging.
- The staging health endpoint does not identify its code revision. Verify Heroku release and target again before future staging checks.
- Actual charges, taxes, and Scheduler one-off cost remain unverified. Keep hosted data synthetic; no live advertiser account, campaign publication, or ad spend is enabled.

## Next action

Select and implement the next small local product UX slice from the blueprint while keeping all inputs and results synthetic; first inspect the current campaign journey and documented open decisions to avoid enabling real advertiser data or external actions. The creative editing/version-history browser review is complete. The stopped synthetic-only rehearsal folder `%TEMP%\gwt_full_rehearsal_a656127cec` still needs cleanup; recursive deletion was blocked by command policy, but this does not prevent local product work.
