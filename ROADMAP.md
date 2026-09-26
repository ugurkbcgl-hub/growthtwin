# Phase 0 roadmap

## M0 — Local project workspace
Status: complete
- Created a separate local Git workspace and project baseline docs.
- Kept the synced project mirror and its sources/ files untouched.

## M1 — Public source-of-truth repository
Status: mostly complete — repository, `main`, issue template, and enforced pull-request protections are in place; required CI checks remain pending.
- Created `ugurkbcgl-hub/growthtwin` as a public repository at the user's request and pushed the baseline.
- `main` is the default branch. Enforced branch protection requires pull requests, applies to administrators, blocks force-pushes and deletion, requires conversation resolution, and requires linear history.
- Use feature branches and pull requests for changes. Add a required CI status check after a CI workflow exists.

## M2 — Development environment and cost decision
Status: pending
- Decide whether WSL2 Ubuntu is a short-term bootstrap or a separate Linux development server is needed now.
- Initial inventory is complete. Ollama 0.34.4 is installed on the Windows workstation; the Qwen3 local smoke evaluation is recorded in AI_PROVIDERS.md.
- No paid infrastructure or recurring service has been enabled.
- Estimate cloud costs and obtain a user decision before a single spend above USD 20 or any recurring service.
- Keep monthly spending under the confirmed project cap.

## M3 — Repository and engineering guardrails
Status: in progress — architecture and guardrail docs plus language-neutral placeholders drafted; stack-dependent CI remains open.
- Keep PROJECT.md aligned with the user's public-repository decision; complete ARCHITECTURE.md, SECURITY.md, TESTING.md, DEPLOYMENT.md, and the ADR process.
- Add only a small repository skeleton; do not create product services prematurely.
- Add formatting, lint, type, unit/integration, security/dependency and build checks to CI after choosing the implementation stack.

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
- CI checks have not been configured, so `main` does not yet require a passing status check.
- The replacement NVIDIA Build API key must stay out of this repository and chat. Account-level and per-model limits have not yet been recorded; check the signed-in Build account before relying on them.
- M2 host and staging/cost decisions, and M3 stack-dependent CI, remain open.
