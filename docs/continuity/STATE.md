# GrowthTwin — current handoff

Last verified: 2026-09-27 17:48 (Europe/Istanbul)

## Goal and working rules

- Complete Phase 0: establish and demonstrate a repeatable, safe development workflow before implementing GrowthTwin product features.
- Product direction: an AI-assisted content, review, publishing, and analytics workflow for dental clinics in Türkiye.
- Keep hosted evaluations synthetic and credentials out of chat and Git. No paid infrastructure or staging service beyond the explicitly approved Heroku plan.

## Repository and review

- Repository: https://github.com/ugurkbcgl-hub/growthtwin (public; `main` is the default branch).
- Local checkout: `C:\Users\Public\Desktop\GrowthTwin`; this handoff update is on `docs/heroku-staging-handoff`, based on clean `main` at `ac2f627` before these documentation edits.
- PR #12 merged as `ac2f627` on 2026-09-27; its required CI run `36319171723` and post-merge `main` CI run `36319239593` passed.
- Main protection requires PR review flow, the passing `Django system check` on an up-to-date branch, conversation resolution, and linear history; force-push and deletion are blocked.
- The owner delegated routine implementation and merge decisions after review and successful required CI.

## Phase 0 status

- M2 is recorded complete. Local PostgreSQL service state and DPAPI-protected credential storage were not rechecked in this session.
- M3 guardrails are complete for the Django shell.
- M4 synthetic profile-edit demo is merged in PR #7. Staging app `growthtwin-stage-270927` is deployed from reviewed `main` commit `ac2f627` at https://growthtwin-stage-270927-9d8c14f4e775.herokuapp.com/.
- Heroku Resources showed one Basic web dyno and one Essential-0 PostgreSQL add-on, estimated at about USD 12/month before taxes. No other paid add-on or dyno was shown. The user approved only this bounded staging setup; delete it after M4 acceptance. Use synthetic data only.
- Heroku reported successful deployment and release phase. A fresh `GET /health/?check=20260927-istanbul-01` returned HTTP 200 with 38 bytes in both router and app logs at 2026-09-27 13:31:50 UTC. The browser tab still displayed an earlier `400` response after a navigation attempt was blocked; the response body and UI/log discrepancy remain unverified.
- The repository has focused Django tests for the profile-edit behavior, but no Playwright end-to-end test was found. Staging profile-edit E2E, backup/restore, and controlled rollback have not been completed.
- Product features, social publishing, and AI provider calls remain out of scope.

## Next action

Add a focused Playwright end-to-end check for the synthetic profile-edit path and define a disposable staging test-account setup that keeps credentials out of source, chat, and logs. Then verify backup/restore and controlled rollback before recording M4 acceptance.

## Not rechecked

- Local PostgreSQL service and DPAPI-protected credential store.
- NVIDIA Build account quotas and current model limits.
- A browser-confirmed health response body, staging E2E, backup/restore, and rollback.
