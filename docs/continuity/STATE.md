# GrowthTwin — current handoff

Last verified: 2026-09-27 19:44 (Europe/Istanbul)

## Goal and working rules

- Complete Phase 0: establish and demonstrate a repeatable, safe development workflow before implementing GrowthTwin product features.
- Product direction: an AI-assisted content, review, publishing, and analytics workflow for dental clinics in Türkiye.
- Use synthetic data for hosted checks. Keep credentials and private data out of chat, Git, logs, and handoff files.
- The only approved paid infrastructure is one Heroku Basic dyno plus one Essential-0 PostgreSQL database, about USD 12/month before taxes. Add no other paid services and delete staging after M4 acceptance.
- Follow the usage-aware handoff protocol in `AGENTS.md` and this folder's `README.md`.

## Repository and review

- Repository: https://github.com/ugurkbcgl-hub/growthtwin (public; `main` is the default branch).
- PR #17, `test: add browser E2E for demo profile`, is open on `m4/profile-edit-playwright-e2e`. Its prior tip `6f51b75` was based on `6464c24`; it conflicted with current main only in this state file.
- Current main before this branch sync: clean `1280204`; PR #16 required and post-merge CI passed. The current branch is being synced with main and the state conflict is resolved.
- PR #17's first CI run `36333159110` failed because Chromium was installed after Django test discovery. A later commit moved browser installation before tests; its fresh CI run is pending after branch synchronization.
- Reviewed the E2E implementation: the reusable flow checks anonymous redirect, login, CSRF-protected synthetic profile edit, persisted values, logout, and access restriction. The staging runner is hardcoded to the approved HTTPS host and reads credentials interactively without saving/logging them.
- Main requires PR flow, passing `Django system check` on an up-to-date branch, resolved conversations, and linear history. The owner delegated routine merge decisions after review and successful required CI.

## Phase 0 status

- M2 local Django/PostgreSQL setup is recorded complete; local service and DPAPI secret store were not rechecked now. M3 guardrails are complete.
- M4 synthetic profile-edit demo is merged (PR #7). Heroku app `growthtwin-stage-270927` was deployed from `main` revision `ac2f627`: https://growthtwin-stage-270927-9d8c14f4e775.herokuapp.com/.
- Heroku Resources previously showed one Basic web dyno and one Essential-0 PostgreSQL add-on, estimated at about USD 12/month. Current allocation has not been rechecked in this session.
- Heroku deployment/release succeeded. Two fresh `/health/` requests returned HTTP 200 with 38 bytes in router/app logs; the browser client blocked fresh navigation and retained an old 400 page, so its body was not visually confirmed. The root route returns 404; the demo route is `/demo/profile/`.
- Locally installed pinned Playwright 1.63.0 and Chromium in the ignored `apps/web/.venv`. `python manage.py test e2e --settings=config.test_settings --verbosity 2` passed: 1 real-browser test using an in-memory SQLite database; Django reported no system-check issues.
- The updated PR CI has not passed yet. A disposable staging account has not been provisioned and staging E2E has not run. Backup/restore, controlled rollback, and final M4 acceptance remain incomplete.
- No product workflows or AI provider calls are in scope.

## Next action

Push the main-synced PR #17 branch, verify its required CI and final diff, and merge by squash only after both pass. Then run staging E2E with a disposable account and verify backup/restore and controlled rollback before M4 acceptance.

## Not rechecked

- Current Heroku dyno/database allocation and browser-visible health body.
- A safe provisioning/cleanup path for the disposable staging account.
- Backup/restore, rollback, local PostgreSQL state, and NVIDIA account/model quotas.
