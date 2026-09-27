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
Status: complete — local Django/PostgreSQL workflow installed and verified; no paid services enabled.
- Python 3.13.15 is installed in the current user's Windows environment. Keep the single Codex-managed checkout in place; do not create a second WSL checkout.
- Ubuntu WSL2 is available for local Linux tooling if needed. WSL is version 2.6.1.0; the distro was stopped at inventory time.
- Windows Node.js 24.11.1/npm 11.6.2 remain available for other tooling. PostgreSQL 18.6 and `psql` are installed locally; the `postgresql-x64-18` service is running on port 5432. Docker CLI was not found in the current session; Node is not needed for the accepted Django server stack.
- `growthtwin` database and restricted `growthtwin_app` role were created. Django migrations and the Django system check passed.
- Local database and Django secrets are protected for this Windows user with DPAPI outside the repository. No credential values are committed.
- Ollama 0.34.4 and the earlier Qwen3 evaluation are recorded in AI_PROVIDERS.md; no more model sweeps are part of M2.
- No paid infrastructure or recurring service has been enabled.
- Estimate cloud costs and obtain a user decision before a single spend above USD 20 or any recurring service.
- Keep monthly spending under the confirmed project cap.

## M3 — Repository and engineering guardrails
Status: complete for the Phase 0 shell — architecture and guardrail docs are in place, and CI checks Django configuration, formatting, linting, dependency vulnerabilities, and Python distributions. Type-checking remains unselected until the application has enough code to benefit from it.
- Keep PROJECT.md aligned with the user's public-repository decision; complete ARCHITECTURE.md, SECURITY.md, TESTING.md, DEPLOYMENT.md, and the ADR process.
- Add only a small repository skeleton; do not create product services prematurely.
- Dependency auditing and package builds run in CI. M4 adds focused Django tests for the synthetic demo; introduce type-checking tooling only when the Python surface area benefits from it.

## M4 — Demo application and deployment chain
Status: in progress — the synthetic profile-edit flow is merged and passed CI against PostgreSQL 18.6. The staging plan is prepared; provisioning remains gated on approval of the recurring charge.
- Build only a small demo profile-edit flow to validate the development factory. Complete (PR #7).
- Recommended staging plan: Heroku Basic web dyno ($7/month) plus Essential-0 Postgres ($5/month), about USD 12/month before taxes or optional services. Heroku currently lists PostgreSQL 18 support. Render's free Postgres expires after 30 days and does not include backups, so it is a poor fit for repeatable staging.
- Shutdown plan: use synthetic data only, avoid paid add-ons, and delete both the Heroku app and database after M4 acceptance to end the recurring charges.
- Provision after the owner approves this recurring-cost plan; then run the critical Playwright path.
- Verify health/readiness checks, logs, versioned deployment, backups, and rollback.

Pricing and provider details were checked 2026-09-27: [Heroku pricing](https://www.heroku.com/pricing/), [Heroku Postgres plans](https://devcenter.heroku.com/articles/heroku-postgres-plans), [Heroku Postgres version support](https://devcenter.heroku.com/articles/heroku-postgres-version-support), and [Render free-tier limits](https://render.com/docs/free).

## M5 — Phase 0 final acceptance
Status: pending
- Exercise a normal feature through issue, branch, PR, CI, merge, staging, E2E, and deployment checks.
- Exercise controlled rollback and a CI failure that blocks merge.
- Record results, costs, risks, and open decisions in PHASE_0_COMPLETION_REPORT.md.
- Do not begin GrowthTwin product features or Phase 1 without the user's explicit go-ahead.

## Current blockers
- The replacement NVIDIA Build API key must stay out of this repository and chat. Account-level and per-model limits have not yet been recorded; check the signed-in Build account before relying on them.
- The staging provider and recurring-cost ceiling remain open for M4.
