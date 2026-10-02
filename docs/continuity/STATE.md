# GrowthTwin — current handoff

Last verified: 2026-10-02 23:56 +0300 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for advertisers in Türkiye across sectors. Keep local product work synthetic. Do not accept real advertiser/customer/patient data, connect live accounts, publish ads, spend media budget, add paid infrastructure, or alter staging as part of this work. Phase 0 recovery, privacy, provider and platform gates still apply before external beta/production use.

## Verified repository state

- Latest verified `main`: `41baf3573cb24606d6d886dd550938d5e7c49565`, merged via PR #193. PR #193 CI `37062771616` and post-merge `main` CI `37063052539` passed, including full Django tests and browser E2E.
- Current continuity refresh is on `docs/continuity-after-pr-193`; delivered as a feature PR, not directly on `main`.
- PR #192 (`c8a66fb`) clarified the difference between a synthetic draft ready for local review and a real campaign ready for publishing. Required CI `37061846991` and post-merge CI `37062126477` passed.
- PR #190 required CI `37060557459` and post-merge CI `37060818702` passed. PR #189 live character counts passed required/post-merge CI `37059568415`, `37059833068`.
- No Heroku or external service action was taken in these changes; recheck staging before future operations.

## Completed

- PR #190 adds owner-scoped restoration of an earlier creative snapshot as a new appended version. History remains intact; only same-source history is eligible; stale, current, unknown, foreign-owner and non-POST requests are rejected; the preferred review selection is cleared. No model/migration change. Local focused 38-test campaign service/view/browser run, Django checks, Ruff, `git diff --check`, required CI and post-merge CI passed.
- PR #192 explains that the campaign page is a synthetic preview: account connection, publishing, spend and real channel metrics are unavailable. It lists launch-readiness conditions without enabling external actions.
- PR #193 refreshes this handoff after PR #192 and records the next safety review.
- The local public homepage at `http://127.0.0.1:8002/` contains a free-text brief and a warning to use synthetic information only; it says the draft is temporarily stored for the browser session and is not sent to AI or an advertising platform. The desktop home page was viewed; the authenticated campaign detail was not manually viewed because it requires a local account. No password was entered or requested. The local server is running on port 8002.

## Open blockers and limits

- Heroku release v14 (`69476a62`) was last verified 2026-10-01; `/health/` returned HTTP 200 but `version: unknown`. Do not assume current deployment or revision without rechecking.
- Isolated synthetic PostgreSQL backup/restore rehearsals passed, but configured-database backup/restore and controlled staging rollback remain unverified. A stopped synthetic rehearsal folder `%TEMP%\gwt_full_rehearsal_a656127cec` remains because cleanup was rejected by command policy. This does not block local synthetic product development; do not try alternate deletion paths.
- Staging app/database/Scheduler resources are unchanged. Actual charges/taxes and one-off Scheduler cost remain unverified. No live account, campaign publication, or ad spend is enabled.

## Next action

Review the public campaign brief form against the real-data readiness boundary in `PROJECT.md`, `ROADMAP.md`, and the service blueprint. Keep local demonstrations usable with synthetic inputs, and make any required boundary clearer or stronger without enabling customer-data intake. Verify the resulting UX through existing synthetic browser coverage.
