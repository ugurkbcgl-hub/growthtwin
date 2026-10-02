# GrowthTwin — current handoff

Last verified: 2026-10-02 23:37 +0300 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for advertisers in Türkiye across sectors. Keep local product work synthetic. Do not accept real advertiser/customer/patient data, connect live accounts, publish ads, spend media budget, add paid infrastructure, or alter staging as part of this work. Phase 0 recovery, privacy, provider and platform gates still apply before external beta/production use.

## Verified repository state

- Latest verified `main`: `909a6892d7ade0085e15f895fd2c25d9aee7e0bf`, merged via PR #191. Its required CI `37061125024` and post-merge CI `37061399507` passed, including full Django tests and browser E2E.
- Current work is PR #192 on `feat/campaign-launch-readiness-explainer`, based on `main`; commit `dafded8` adds a local campaign-readiness explanation. Required CI is being checked; verify live status before merging.
- PR #190 required CI `37060557459` and post-merge CI `37060818702` passed. PR #189 added live creative character counts; CI `37059568415` and `37059833068` passed.
- No Heroku or external service action was taken during this work. Recheck staging before any future operation.

## Completed

- PR #190 adds owner-scoped restoration of an earlier creative snapshot as a new appended version. Existing history is preserved; only same-source history is eligible; stale, current, unknown, foreign-owner and non-POST attempts are rejected; the preferred review selection is cleared. No model or migration changes.
- Local focused validation for #190: 38 campaign service/view and browser-workspace tests passed on in-memory SQLite; Django checks, Ruff, and `git diff --check` passed. Required and post-merge CI passed.
- PR #192 clarifies that a complete synthetic draft is ready only for local review, lists future launch-readiness conditions in plain Turkish, and explicitly says account connection, publishing, spending and real platform metrics are not available in this prototype. It does not enable external actions.

## Open blockers and limits

- Heroku release v14 (`69476a62`) was last verified 2026-10-01; `/health/` returned HTTP 200 but `version: unknown`. Do not assume current deployment or revision without rechecking.
- Isolated synthetic PostgreSQL backup/restore rehearsals passed, but configured-database backup/restore and controlled staging rollback remain unverified. A stopped synthetic rehearsal folder `%TEMP%\gwt_full_rehearsal_a656127cec` remains because cleanup was rejected by command policy. This does not block local synthetic product development; do not try alternate deletion paths.
- Staging app/database/Scheduler resources are unchanged. Actual charges/taxes and one-off Scheduler cost remain unverified. No live account, campaign publication or ad spend is enabled.

## Next action

Review PR #192, verify its required CI, merge only if the change is clean and CI passes, then verify post-merge `main` CI. Continue with one small local synthetic UX slice from the service blueprint; keep external integrations and real data outside scope.
