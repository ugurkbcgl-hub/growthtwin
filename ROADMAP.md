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
Status: in progress — architecture/guardrail docs and Django module skeleton are merged; the required CI now checks Django configuration, Python formatting, and linting. This M3 step adds a pinned dependency vulnerability audit.
- Keep PROJECT.md aligned with the user's public-repository decision; complete ARCHITECTURE.md, SECURITY.md, TESTING.md, DEPLOYMENT.md, and the ADR process.
- Add only a small repository skeleton; do not create product services prematurely.
- Add a dependency vulnerability audit to CI. Add type, unit/integration, and build checks as their tooling and testable application behavior are established.

## M4 — Demo application and deployment chain
Status: pending
- Build only a small demo profile-edit flow to validate the development factory.
- Deploy the demo to staging; run its critical Playwright path.
- Verify health/readiness checks, logs, versioned deployment, backups, and rollback.

## M5 — Phase 0 final acceptance
Status: pending
- Exercise a normal feature through issue, branch, PR, CI, merge, staging, E2E, and deployment checks.
- Exercise controlled rollback and a CI failure that blocks merge.
- Record results, costs, risks, and open decisions in PHASE_0_COMPLETION_REPORT.md.
- Do not begin GrowthTwin product features or Phase 1 without the user's explicit go-ahead.

## Current blockers
- The replacement NVIDIA Build API key must stay out of this repository and chat. Account-level and per-model limits have not yet been recorded; check the signed-in Build account before relying on them.
- The staging provider and recurring-cost ceiling remain open for M4.
