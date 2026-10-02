# GrowthTwin — current handoff

Last verified: 2026-10-02 23:46 +0300 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for advertisers in Türkiye across sectors. Keep local product work synthetic. Do not accept real advertiser/customer/patient data, connect live accounts, publish ads, spend media budget, add paid infrastructure, or alter staging as part of this work. Phase 0 recovery, privacy, provider and platform gates still apply before external beta/production use.

## Verified repository state

- Latest verified `main`: `c8a66fb44cfcb7875d9d9787c81a56fe2ebc17e4`, merged via PR #192. Required CI `37061846991` and post-merge `main` CI `37062126477` passed, including full Django tests and browser E2E.
- Current continuity refresh is on feature branch `docs/continuity-after-pr-192`; it will be submitted as PR #193. Do not push directly to `main`.
- PR #191 post-merge CI `37061399507` and PR #190 post-merge CI `37060818702` passed. PR #189 added live character counts; required and post-merge CI `37059568415`, `37059833068` passed.
- No Heroku or external service action was taken. Recheck staging before future operations.

## Completed

- PR #190 adds owner-scoped restoration of an earlier creative snapshot as a new appended version. History remains intact; only same-source history is eligible; stale, current, unknown, foreign-owner and non-POST requests are rejected; the preferred review selection is cleared. No model/migration change. Local focused 38-test campaign service/view/browser run, Django checks, Ruff, `git diff --check`, required CI and post-merge CI passed.
- PR #192 distinguishes a synthetic draft ready for local review from a real campaign ready to publish. The campaign page explains in Turkish that account connection, publishing, spend, and real channel metrics are not available, and lists future readiness conditions. No external capability was added. Required and post-merge CI passed.
- The local public homepage observed at `http://127.0.0.1:8002/` contains a free-text brief and an on-page warning to use synthetic information only; it says the draft is temporarily stored for the browser session and is not sent to AI or an advertising platform. This behavior should be compared carefully with the project's real-data readiness gate before changing intake.

## Open blockers and limits

- Heroku release v14 (`69476a62`) was last verified 2026-10-01; `/health/` returned HTTP 200 but `version: unknown`. Do not assume current deployment or revision without rechecking.
- Isolated synthetic PostgreSQL backup/restore rehearsals passed, but configured-database backup/restore and controlled staging rollback remain unverified. A stopped synthetic rehearsal folder `%TEMP%\gwt_full_rehearsal_a656127cec` remains because cleanup was rejected by command policy. This does not block local synthetic product development; do not try alternate deletion paths.
- Staging app/database/Scheduler resources are unchanged. Actual charges/taxes and one-off Scheduler cost remain unverified. No live account, campaign publication, or ad spend is enabled.

## Next action

Review the public campaign brief form against the real-data readiness boundary in `PROJECT.md`, `ROADMAP.md`, and the service blueprint. Keep local demonstrations usable with synthetic inputs, and make any required boundary clearer or stronger without enabling customer-data intake. Verify the resulting UX through existing synthetic browser coverage.
