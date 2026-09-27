# Phase 0 roadmap

## M0 — Local project workspace
Status: complete
- Created a separate local Git workspace and project baseline docs.
- Kept the synced project mirror and its sources/ files untouched.

## M1 — Public source-of-truth repository
Status: mostly complete — repository, `main`, issue template, pull-request protections, and the required CI status check are in place.
- Created `ugurkbcgl-hub/growthtwin` as a public repository at the user's request and pushed the baseline.
- `main` is the default branch. Enforced branch protection requires pull requests, applies to administrators, blocks force-pushes and deletion, requires conversation resolution and linear history, and requires the passing `Django system check` from GitHub Actions on an up-to-date branch.
- Use feature branches and pull requests for changes.

## M2 — Development environment and cost decision
Status: complete — local Django/PostgreSQL workflow installed and verified; no paid services enabled at the time M2 was completed.
- Python 3.13.15 is installed in the current user's Windows environment. Keep the single Codex-managed checkout in place; do not create a second WSL checkout.
- Ubuntu WSL2 is available for local Linux tooling if needed. WSL is version 2.6.1.0; the distro was stopped in the last inventory.
- Windows Node.js 24.11.1/npm 11.6.2 remain available for other tooling. PostgreSQL 18.6 and `psql` are installed locally; the `postgresql-x64-18` service was running in the last inventory. Docker CLI was not found in that inventory; Node is not needed for the accepted Django server stack.
- `growthtwin` database and restricted `growthtwin_app` role were created. Earlier Django migrations and the Django system check passed.
- Local database and Django secrets are protected for this Windows user with DPAPI outside the repository. No credential values are committed.
- Ollama 0.34.4 and the earlier Qwen3 evaluation are recorded in AI_PROVIDERS.md; no more model sweeps are part of this setup step.
- Heroku staging was separately approved for M4 at approximately USD 12/month before taxes. Keep spending within that one Basic dyno + one Essential-0 database limit; no additional paid services are authorized.

## M3 — Repository and engineering guardrails
Status: complete for the Phase 0 shell — architecture and guardrail docs are in place, and CI checks Django configuration, formatting, linting, dependency vulnerabilities, and Python distributions. Type-checking remains unselected until the application has enough code to benefit from it.
- Keep PROJECT.md aligned with the user's public-repository decision; complete ARCHITECTURE.md, SECURITY.md, TESTING.md, DEPLOYMENT.md, and the ADR process.
- Add only a small repository skeleton; do not create product services prematurely.
- Dependency auditing and package builds run in CI. M4 adds focused Django tests for the synthetic demo; introduce type-checking tooling only when the Python surface area benefits from it.

## M4 — Demo application and deployment chain
Status: in progress — the synthetic profile-edit flow is merged and passed CI (PR #7); the approved Heroku staging app is deployed. Staging E2E, backup/restore, and rollback checks remain.
- Build only a small demo profile-edit flow to validate the development factory. Complete (PR #7).
- Provisioning complete: `growthtwin-stage-270927` has one Heroku Basic web dyno and one Essential-0 PostgreSQL database. Resources screen estimated about USD 12/month before taxes; no other paid resource was shown.
- Last recorded deployment: connected GitHub repository `ugurkbcgl-hub/growthtwin`, branch `main`, revision `ac2f627` deployed on 2026-09-27; Heroku reported deployment and release phase success. Deployment of newer `main` commit `f2973b6` has not been checked. App: https://growthtwin-stage-270927-9d8c14f4e775.herokuapp.com/.
- Health checks: Heroku router/app logs recorded an earlier HTTP 200 response. A follow-up direct PowerShell `GET /health/?check=20260927-followup-01` returned HTTP 200 with `{"status": "ok", "version": "unknown"}`. Database readiness is confirmed; deployed revision and browser-visible behavior remain unverified.
- A pinned Playwright browser test covers the synthetic profile flow against an isolated local Django test server; the local run passed. PR #17 merged as `f2973b6`; its required CI run `36334388490` and post-merge main CI run `36334519381` both passed. It adds the test to CI and a staging runner that prompts for a disposable account without saving its password.
- Staging browser E2E remains pending because no disposable account has been provisioned. The app exposes no public signup or Django admin route; use a provisioning method within the approved resource limit. Verify login/CSRF/redirect behavior on the approved staging hostname, then delete the disposable account and profile.
- Then verify backup/restore and controlled rollback; record their actual results before M4 acceptance.
- Shutdown plan: delete the app and database after M4 acceptance to end recurring charges.

## M5 — Phase 0 final acceptance
Status: pending
- Exercise a CI failure that blocks merge and a controlled rollback.
- Record verified results, costs, risks, and open decisions in PHASE_0_COMPLETION_REPORT.md.
- Do not begin GrowthTwin product features or Phase 1 without the user's explicit go-ahead.

Pricing and provider details were checked 2026-09-27: [Heroku pricing](https://www.heroku.com/pricing/), [Heroku Postgres plans](https://devcenter.heroku.com/articles/heroku-postgres-plans), [Heroku Postgres version support](https://devcenter.heroku.com/articles/heroku-postgres-version-support), and [Render free-tier limits](https://render.com/docs/free).

## Current blockers

- Phase 0 M4 acceptance remains incomplete: provision a disposable staging account safely and run profile-edit E2E, confirm the health response and deployed revision, and verify backup/restore and rollback.
- The replacement NVIDIA Build API key must stay out of this repository and chat. Account-level and per-model limits have not been recorded; check the signed-in Build account before relying on them.
