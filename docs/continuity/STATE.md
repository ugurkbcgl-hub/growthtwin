# GrowthTwin — current handoff

Last verified: 2026-09-30 23:02 +0300 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` baseline after PR #177: `91a6ed3dc980501cf291c9b434c5a226173fbcdd`. Required PR CI `36769327328` and post-merge CI `36769631164` passed. `main` branch protection is enabled with required check `Django system check`, up-to-date PR branches, and admin enforcement.
- This state refresh is delivered via the feature-branch/PR workflow. Recheck live branch, worktree, open PRs, and CI before future actions; do not push directly to `main`.
- Heroku staging release v14 deploys `69476a62` (2026-09-30). `/health/` returned HTTP 200 with `version: unknown`; runtime revision reporting remains unresolved. Releases v11–v13 updated database and Django secret configuration; secret values are not recorded here.
- Existing approved staging resources remain the Basic web dyno, Essential-0 PostgreSQL, and Standard Free Scheduler. Previously observed estimate is about USD 12/month before tax; actual billing and one-off Scheduler dyno cost remain unverified. No resource was added.

## Completed

- Created and verified a disposable, active staging user `growthtwin-e2e-20260930` with normal user permissions (`staff=False`, `superuser=False`). Its synthetic profile is `GrowthTwin E2E Sentetik Klinik`, `Test Şehri`, `0000000000`, and `https://example.invalid`.
- Against staging release v14, the profile-edit browser flow passed: unauthenticated redirect, login, synthetic profile save, persistence after reload, logout, and protected-route check after logout. It reused `e2e.profile_edit_flow.run_profile_edit_flow` through a one-time local helper. The password is not stored in Git, docs, logs, or this handoff; the owner manages it.
- Confirmed GitHub main CI `36750735813` passed for PR #176. PR #177 updated PROJECT, ROADMAP, and the Phase 0 staging verification sequence; it was merged after local review and passing required CI. Post-merge CI passed. No backup/restore or rollback was performed.

## Open blockers and limits

- Backup/restore and controlled rollback remain unverified. Do not restore over the only staging database until a non-destructive target and recovery order are established.
- The staging health endpoint does not identify its code revision. Verify Heroku release and target again before future staging checks.
- Actual charges, taxes, and Scheduler one-off cost remain unverified. Keep hosted data synthetic; no live advertiser account, campaign publication, or ad spend is enabled.

## Next action

Plan a non-destructive synthetic-only backup/restore rehearsal: verify the current database plan's recovery capabilities and document a safe restore target and recovery order. Do not restore until a safe target is established.
