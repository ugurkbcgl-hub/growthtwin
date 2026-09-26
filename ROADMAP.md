# Phase 0 roadmap

## M0 — Local project workspace
Status: complete
- Created a separate local Git workspace and project baseline docs.
- Kept the synced project mirror and its sources/ files untouched.

## M1 — Private source-of-truth repository
Status: pending
- Create or connect the private GitHub repository named growthtwin.
- Connect this local repository to the authorized remote.
- Set main as the default branch; protect it from direct pushes and require passing CI.
- Add issue templates and establish issue-first work tracking.

## M2 — Development environment and cost decision
Status: pending
- Decide whether WSL2 Ubuntu is a short-term bootstrap or a separate Linux development server is needed now.
- Inventory Ubuntu, GPU passthrough, disk, and installed tools before installing anything.
- Estimate cloud costs and obtain a user decision before a single spend above USD 20 or any recurring service.
- Keep monthly spending under the confirmed project cap.

## M3 — Repository and engineering guardrails
Status: pending
- Complete PROJECT.md, ARCHITECTURE.md, SECURITY.md, TESTING.md, DEPLOYMENT.md, and ADR process.
- Add a small repository skeleton only; do not create product services prematurely.
- Add formatting, lint, type, unit/integration, security/dependency and build checks to CI.

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
- The initial scaffold is not committed because Git author identity is not configured.
- No remote GitHub repository or authenticated GitHub CLI is available in this workspace yet.
- The NVIDIA Build API key in the supplied screenshot should be revoked and replaced before use. The replacement key must stay out of this repository and chat.
- The account-specific NVIDIA model limits are not visible from the screenshot; check them in the signed-in Build account.
