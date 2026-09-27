# GrowthTwin — current handoff

Last verified: 2026-09-27 18:17 (Europe/Istanbul)

## Goal and working rules

- Complete Phase 0: establish and demonstrate a repeatable, safe development workflow before implementing GrowthTwin product features.
- Product direction: an AI-assisted content, review, publishing, and analytics workflow for dental clinics in Türkiye.
- Keep hosted evaluations synthetic and credentials out of chat and Git. The only approved paid service is the bounded Heroku staging setup described below.
- Low-usage handoff: `AGENTS.md` and this folder's `README.md` now define an early-preparation threshold of 10% remaining and completion by 5%. The active Codex heartbeat checks hourly and stays quiet unless work is needed.

## Repository and review

- Repository: https://github.com/ugurkbcgl-hub/growthtwin (public; `main` is the default branch).
- At snapshot time, local `main` was clean at `57b69c3`; this state refresh is on `docs/low-usage-handoff-snapshot` based on that commit.
- PR #13 merged as `4a2e86e`; its required and post-merge main CI passed. PR #14 merged as `57b69c3`; its required CI run `36328827264` and post-merge `main` CI run `36328912152` passed.
- Main protection requires the PR flow, successful `Django system check` on an up-to-date branch, resolved conversations, and linear history; force-push and deletion are blocked.
- The owner delegated routine implementation and merge decisions after review and successful required CI.

## Phase 0 status

- M2 is recorded complete. Local PostgreSQL service and DPAPI-protected credential storage were not rechecked in this session.
- M3 guardrails are complete for the Django shell.
- M4 synthetic profile-edit demo is merged in PR #7. Staging app `growthtwin-stage-270927` is deployed from reviewed `main` commit `ac2f627` at https://growthtwin-stage-270927-9d8c14f4e775.herokuapp.com/.
- Heroku Resources showed one Basic web dyno and one Essential-0 PostgreSQL add-on, estimated at about USD 12/month before taxes. No other paid add-on or dyno was shown. Delete the app and database after M4 acceptance. Use synthetic data only.
- Heroku deployment and release phase succeeded. Fresh `GET /health/` requests at 2026-09-27 13:31:50 UTC and 14:57:12 UTC returned HTTP 200 with 38 bytes in router/app logs. The browser client blocked fresh navigation and retained an old `400` page, so the body was not visible in the browser. The root `/` route returns 404; the documented demo path is `/demo/profile/`.
- The repo has focused Django profile-edit tests but no Playwright E2E. Staging profile-edit E2E, backup/restore, and controlled rollback have not been completed.
- Product features, social publishing, and AI provider calls remain out of scope.

## Next action

Implement and run a focused Playwright E2E for the synthetic `/demo/profile/` flow using a disposable staging test account and a credential-safe setup. Then verify backup/restore and controlled rollback, record actual results, and complete M4 acceptance before deleting the approved staging resources.

## Not rechecked

- Local PostgreSQL service and DPAPI-protected credential store.
- NVIDIA Build account quotas and current model limits.
- Browser-visible health response body, staging E2E, backup/restore, and rollback.
