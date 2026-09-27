# GrowthTwin — current handoff

Last verified: 2026-09-27 14:24 (Europe/Istanbul)

## Goal and working rules

- Complete Phase 0: establish and demonstrate a repeatable, safe development workflow before implementing GrowthTwin product features.
- Product direction: an AI-assisted content, review, publishing, and analytics workflow for dental clinics in Türkiye.
- Keep hosted evaluations synthetic and credentials out of chat and Git. No paid infrastructure or staging service without an explicit approved plan.

## Repository and review

- Repository: https://github.com/ugurkbcgl-hub/growthtwin (public; main is the default branch).
- Checkout: C:\Users\Public\Desktop\GrowthTwin, on branch m4/demo-profile-edit.
- PR #3 merged as 394d3d4; post-merge CI passed.
- PR #4 merged as 2f53376; post-merge CI passed with the Django check, Ruff formatting, and Ruff lint.
- PR #5 merged as 580d972; post-merge CI passed with dependency auditing.
- PR #6 merged as 60e3e92; post-merge CI passed with the source and wheel build checks.
- PR #7 is open on m4/demo-profile-edit. Commit 5352054 passed required CI, including formatting, lint, dependency audit, distribution content checks, Django system check, migration consistency, and Django tests against PostgreSQL 18.6.
- main protection requires a PR and the Django system check from GitHub Actions on an up-to-date branch; it also requires linear history and conversation resolution, applies to administrators, and blocks force-push and deletion.
- Use feature branches and PRs. The user has delegated routine project decisions, including merges after review and successful required CI.

## Phase 0 status

- M2 is recorded complete in the roadmap. Local PostgreSQL service state and protected credential storage were not checked in this turn.
- M3 guardrails are complete for the Django shell: architecture/docs, required configuration check, Ruff format/lint, dependency audit, and source/wheel build verification are in main. A type checker remains unselected until the codebase benefits from one.
- M4 synthetic profile-edit demo is in PR #7. Four local tests passed using the isolated in-memory SQLite test settings; PR CI passed the same behavior tests against ephemeral PostgreSQL 18.6. The build verifies both archives contain the demo templates.
- The staging provider and cost ceiling remain open; this work did not enable a staging service. Product feature implementation, social publishing, and AI provider calls remain out of scope.

## Next action

After PR #7 is merged, compare suitable staging options and current costs. Present a concrete provider, monthly estimate, and shutdown plan; obtain the required approval before provisioning any staging or paid service. Keep all demo data synthetic.

## Not rechecked

- Local PostgreSQL service and the DPAPI-protected credential store.
- NVIDIA Build account quotas and current model limits.
- Staging provider pricing and recurring-cost estimate.
