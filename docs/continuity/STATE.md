# GrowthTwin — current handoff

Last verified: 2026-10-02 23:32 +0300 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for advertisers in Türkiye across sectors. Keep local product work synthetic. Do not accept real advertiser/customer/patient data, connect live accounts, publish ads, spend media budget, add paid infrastructure, or alter staging as part of this work. Phase 0 recovery, privacy, provider and platform gates still apply before external beta/production use.

## Verified repository state

- Latest verified `main`: `4b5c769996ee5a5aabda83a9c88e4fac0890aec9`, merged via PR #190. The code working tree was clean immediately after merge; continuity update is in PR #191 on feature branch `docs/continuity-after-pr-190`, not directly on `main`.
- PR #190 required CI run `37060557459` and post-merge `main` CI run `37060818702` passed, including full Django tests and browser E2E.
- PR #189 (`6a028ab`) added live character counts to creative inputs; required and post-merge CI passed (`37059568415`, `37059833068`).
- No Heroku or external service action was taken during these changes. Most recently verified staging notes remain those below; recheck before any future staging operation.

## Completed

- PR #190 adds owner-scoped restoration of an earlier creative snapshot as a new appended version. Existing history is preserved; only same-source history is eligible; stale, current, unknown, foreign-owner and non-POST attempts are rejected; preferred review selection is cleared. No model or migration changes.
- Local focused validation for #190: 38 campaign service/view and browser-workspace tests passed on in-memory SQLite; Django checks, Ruff, and `git diff --check` passed. Required CI also passed.
- Browser E2E covers editing then restoring a version, preservation of history, and narrow/desktop overflow checks.

## Open blockers and limits

- Heroku release v14 (`69476a62`) was last verified 2026-10-01; `/health/` returned HTTP 200 but `version: unknown`. Do not assume current deployment or revision without rechecking.
- The isolated synthetic PostgreSQL backup/restore rehearsals passed, but configured-database backup/restore and controlled staging rollback remain unverified. A stopped synthetic rehearsal folder `%TEMP%\gwt_full_rehearsal_a656127cec` remains because cleanup was rejected by command policy. This does not block local synthetic product development; do not try alternate deletion paths.
- Staging app/database/Scheduler resources are unchanged. Actual charges/taxes and one-off Scheduler cost remain unverified. No live account, campaign publication or ad spend is enabled.

## Next action

Review the current campaign journey and service-blueprint open decisions, then select and implement one small local synthetic UX slice. Keep external integration and real data outside scope.
