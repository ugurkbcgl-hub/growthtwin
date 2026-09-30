# GrowthTwin — current handoff

Last verified: 2026-09-30 22:57 +0300 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` baseline before this documentation update: `69476a62d2d289761d1aeef8c672e66dadc28b6d` (PR #176). Latest main CI run `36750735813` passed. `main` branch protection is enabled with required check `Django system check`, up-to-date PR branches, and admin enforcement. No open PRs were listed before this update.
- Current worktree is feature branch `docs/staging-e2e-verified`; PR #177 contains the verified staging documentation update. Check the live PR and CI status before taking further action. Do not push directly to `main`.
- Heroku staging release v14 deploys `69476a62` (2026-09-30). `/health/` returned HTTP 200 with `version: unknown`; runtime revision reporting remains unresolved. Releases v11–v13 updated database and Django secret configuration; secret values are not recorded here.
- Existing approved staging resources remain the Basic web dyno, Essential-0 PostgreSQL, and Standard Free Scheduler. Previously observed estimate is about USD 12/month before tax; actual billing and one-off Scheduler dyno cost remain unverified. No resource was added.

## Completed

- Created and verified a disposable, active staging user `growthtwin-e2e-20260930` with normal user permissions (`staff=False`, `superuser=False`). Its synthetic profile is `GrowthTwin E2E Sentetik Klinik`, `Test Şehri`, `0000000000`, and `https://example.invalid`.
- Against staging release v14, the profile-edit browser flow passed: unauthenticated redirect, login, synthetic profile save, persistence after reload, logout, and protected-route check after logout. It reused `e2e.profile_edit_flow.run_profile_edit_flow` through a one-time local helper. The password is not stored in Git, docs, logs, or this handoff; the owner manages it.
- Confirmed GitHub main CI `36750735813` passed. No backup/restore or rollback was performed.
- Updated PROJECT, ROADMAP, and the Phase 0 staging verification sequence to reflect the verified E2E result; changes are on the feature branch for PR review.

## Open blockers and limits

- Backup/restore and controlled rollback remain unverified. Do not restore over the only staging database until a non-destructive target and recovery order are established.
- The staging health endpoint does not identify its code revision. Verify Heroku release and target again before future staging checks.
- Actual charges, taxes, and Scheduler one-off cost remain unverified. Keep hosted data synthetic; no live advertiser account, campaign publication, or ad spend is enabled.

## Next action

After PR #177's required CI passes, merge it under the owner's standing authorization, then plan a non-destructive synthetic-only backup/restore rehearsal using the current database plan; do not perform a restore until a safe target and recovery order are established.
