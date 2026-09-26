# Phase 0 roadmap

## M0 — Local project workspace
Status: complete
- Created a separate local Git workspace and project baseline docs.
- Kept the synced project mirror and its sources/ files untouched.

## M1 — Private source-of-truth repository
Status: partially complete — private repository, authorized connection, initial push, `main` default branch, and issue template are in place.
- Created the private GitHub repository `ugurkbcgl-hub/growthtwin` and pushed the baseline.
- Use feature branches and pull requests as the working convention.
- Enforced branch protection and required CI are pending: GitHub returned HTTP 403 because this private repository needs GitHub Pro for branch protection. Keep the repository private; do not change visibility to public to bypass this limit. Revisit the plan only after reviewing the recurring cost.

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
- `main` is not protected by GitHub because the current account plan does not allow branch protection on a private repository. CI checks have not been configured yet.
- The NVIDIA Build API key in the supplied screenshot should be revoked and replaced before use. The replacement key must stay out of this repository and chat.
- The account-specific NVIDIA model limits are not visible from the screenshot; check them in the signed-in Build account.
