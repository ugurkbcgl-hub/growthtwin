# GrowthTwin — current handoff

Last verified: 2026-09-27 19:49 (Europe/Istanbul)

## Goal and working rules

- Complete Phase 0: establish and demonstrate a repeatable, safe development workflow before implementing GrowthTwin product features.
- Product direction: an AI-assisted content, review, publishing, and analytics workflow for dental clinics in Türkiye.
- Use synthetic data for hosted checks. Keep credentials and private data out of chat, Git, logs, and handoff files.
- The only approved paid infrastructure is one Heroku Basic dyno plus one Essential-0 PostgreSQL database, about USD 12/month before taxes. Add no other paid services and delete staging after M4 acceptance.
- Follow the usage-aware handoff protocol in `AGENTS.md` and this folder's `README.md`.

## Repository and review

- Repository: https://github.com/ugurkbcgl-hub/growthtwin (public; `main` is the default branch).
- Last verified `main` commit: `f2973b6`, the squash merge of PR #17, `test: add browser E2E for demo profile`.
- PR #17 required CI run `36334388490` passed. Post-merge main CI run `36334519381` also passed.
- The PR adds a pinned Playwright browser test for anonymous redirect, login, synthetic profile save, persistence after reload, logout, and access restriction. Its staging runner prompts for credentials without saving them and is restricted to the approved HTTPS hostname.
- The local browser test passed in the prior session using an in-memory SQLite test database. The CI run includes the browser test against its ephemeral PostgreSQL service.
- No open PRs were listed immediately after PR #17 merged. The documentation refresh is being prepared on `docs/refresh-m4-status-after-pr17`.
- The owner delegated routine merge decisions after review and successful required CI. Keep using feature branches and PRs; never push directly to `main`.

## Phase 0 status

- M2 local Django/PostgreSQL setup is recorded complete; local service and DPAPI secret store were not rechecked. M3 guardrails are complete.
- M4 synthetic profile-edit demo is merged (PR #7). The last recorded Heroku deployment was revision `ac2f627`; whether the app has deployed newer `main` commit `f2973b6` is unverified.
- Heroku Resources previously showed one Basic web dyno and one Essential-0 PostgreSQL add-on, estimated at about USD 12/month. Current allocation has not been rechecked.
- A direct PowerShell GET to `/health/?check=20260927-followup-01` returned HTTP 200 with `{"status": "ok", "version": "unknown"}`. Database readiness is confirmed; the endpoint did not report a deployment revision. Browser-visible response has not been rechecked.
- The staging browser E2E has not run. The app exposes no public signup or Django admin route, and a disposable account has not been provisioned. Do not place credentials in chat, CLI arguments, environment variables, logs, files, or PRs.
- Backup/restore and controlled rollback have not been verified. Final M4 acceptance remains incomplete. No product workflows or AI provider calls are in scope.

## Next action

Establish a safe way to provision and remove one disposable staging login within the approved resource limit, then run the existing staging E2E with synthetic profile values. If provisioning would require an additional paid dyno, obtain approval before doing it.

## Not rechecked

- Current Heroku dyno/database allocation and deployed release commit.
- Browser-visible health response, staging E2E, and disposable-account cleanup.
- Backup/restore, rollback, local PostgreSQL state, and NVIDIA account/model quotas.
