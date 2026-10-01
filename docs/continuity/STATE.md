# GrowthTwin — current handoff

Last verified: 2026-10-01 18:47 +0300 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Before this documentation update, clean `main` was at `6bdb0f7eae15891d3532f2deeaf38c6fde866d96` (PR #178); latest main CI `36770390671` passed. No open PRs were listed. `main` branch protection is enabled with required check `Django system check`, up-to-date PR branches, and admin enforcement.
- This state refresh is delivered via the feature-branch/PR workflow. Recheck live branch, worktree, open PRs, and CI before future actions; do not push directly to `main`.
- Heroku staging release v14 deploys `69476a62` (2026-09-30). `/health/` returned HTTP 200 with `version: unknown`; runtime revision reporting remains unresolved. Releases v11–v13 updated database and Django secret configuration; secret values are not recorded here.
- Existing approved staging resources remain the Basic web dyno, Essential-0 PostgreSQL, and Standard Free Scheduler. Previously observed estimate is about USD 12/month before tax; actual billing and one-off Scheduler dyno cost remain unverified. No resource was added.

## Completed

- Created and verified a disposable, active staging user `growthtwin-e2e-20260930` with normal user permissions (`staff=False`, `superuser=False`). Its synthetic profile is `GrowthTwin E2E Sentetik Klinik`, `Test Şehri`, `0000000000`, and `https://example.invalid`.
- Against staging release v14, the profile-edit browser flow passed: unauthenticated redirect, login, synthetic profile save, persistence after reload, logout, and protected-route check after logout. It reused `e2e.profile_edit_flow.run_profile_edit_flow` through a one-time local helper. The password is not stored in Git, docs, logs, or this handoff; the owner manages it.
- Confirmed GitHub main CI `36750735813` passed for PR #176. PR #177 updated PROJECT, ROADMAP, and the Phase 0 staging verification sequence; it was merged after local review and passing required CI. Post-merge CI passed. No backup/restore or rollback was performed.
- On 2026-10-01, the authenticated Heroku CLI reported no staging backups, restores, or copies. The workstation has PostgreSQL 18.6 `pg_restore`; the C: volume reports about 680 GB free. No backup capture, download, restore, or paid resource creation was performed. Heroku documents Essential plan optional daily PGBackups (7 daily/1 weekly retention), no Essential fork/rollback, restore as full target replacement, and US storage for logical dumps. Capture remains deferred until staging data is verified synthetic-only, US storage is accepted, and cost fits the approved budget.

## Open blockers and limits

- Backup/restore and controlled rollback remain unverified. Do not restore over the only staging database until a non-destructive target and recovery order are established.
- The staging health endpoint does not identify its code revision. Verify Heroku release and target again before future staging checks.
- Actual charges, taxes, and Scheduler one-off cost remain unverified. Keep hosted data synthetic; no live advertiser account, campaign publication, or ad spend is enabled.

## Next action

Before any PGBackup capture, verify staging contains only synthetic data, confirm US backup storage is acceptable, and confirm capture usage remains within the approved budget; then restore only into a new isolated local PostgreSQL database, never staging.
