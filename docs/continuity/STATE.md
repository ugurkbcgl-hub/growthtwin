# GrowthTwin — current handoff

Last verified: 2026-09-27 19:25 (Europe/Istanbul)

## Goal and working rules

- Complete Phase 0 before building GrowthTwin product features.
- Product direction: an AI-assisted content, review, publishing, and analytics workflow for dental clinics in Türkiye.
- The owner wants the assistant to coordinate tasks, use subagents when useful and allowed, track their results, and give concise Turkish updates. Avoid making the owner do routine terminal work.
- Prefer fit-for-purpose AI over Turkish-language specialization. Keep model/provider choices replaceable; use synthetic data for hosted trials.
- Do not expose credentials or private data. Do not exceed the approved Heroku staging resources or use additional paid services.

## Repository and review

- Repository: `https://github.com/ugurkbcgl-hub/growthtwin` (public).
- Current branch: `m4/profile-edit-playwright-e2e`, created from `origin/main` at `6464c24`.
- PR #17 is open against `main`: [test: add browser E2E for demo profile](https://github.com/ugurkbcgl-hub/growthtwin/pull/17).
- PR head at creation: `3fd926c` (`test: add browser E2E for demo profile`). This handoff snapshot is being added after that implementation commit; verify the live PR head and branch status.
- Required `Django system check` for PR #17 was pending at the last check (run `36333159110`). Do not claim CI passed. PR #3 and PR #15 are merged.
- Never push directly to `main`. Follow repository review and merge rules; do not merge PR #17 until its required checks pass and it has been reviewed.

## Phase 0 status and verified progress

- M2 local Django/PostgreSQL setup is complete. M3 guardrails and baseline CI are complete.
- M4 is in progress. Heroku staging is approved for one Basic web dyno and one Essential-0 PostgreSQL database (about USD 12/month before taxes); no other paid services are approved. Delete both after M4 acceptance.
- The current staging health URL returned HTTP 200 with a 38-byte response during this session. Browser-visible health output and current Heroku resource allocation still need checking.
- PR #17 adds pinned Playwright 1.63.0, a browser flow for login, profile save, persistence, and logout, an isolated local E2E test in CI, and a staging runner that prompts for credentials without saving or logging them.
- Local `python manage.py test e2e --settings=config.test_settings` passed (1 test). `ruff format --check .`, `ruff check .`, and `git diff --check` passed after the import-order fix. The local test emitted a non-failing warning that the staticfiles directory was absent.
- Actual staging browser E2E has not run. It needs a disposable, least-privilege staging user. No Heroku CLI was available in this host's PATH; find a safe one-off provisioning path before asking the owner to perform terminal steps.
- Backup/restore, controlled rollback, and final M4 report remain incomplete. No GrowthTwin product workflows or AI provider calls are in scope.
- The Codex usage tool reported 97% used / 3% remaining. NVIDIA account/model quota remains unverified. Recheck current usage at the next session; preserve low-usage handoff rules.

## Next action

Check PR #17's required CI result and review it. Fix any failure; merge only after required CI passes and review is complete. Then resume the staging E2E with a disposable user, followed by backup/restore and rollback verification.

## Recheck at the next session

Verify current Codex usage, branch/worktree/PR state, and CI. If staging is needed, verify the app is reachable and still uses only its approved resources. The staging runner is `python -m e2e.run_staging` from `apps/web`; it is restricted to the approved Heroku hostname and asks for the disposable username/password interactively, with the password hidden. Do not put credentials in a command, environment variable, file, trace, log, or GitHub PR.
