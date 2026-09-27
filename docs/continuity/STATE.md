# GrowthTwin — current handoff

Last verified: 2026-09-27 14:41 (Europe/Istanbul)

## Goal and working rules

- Complete Phase 0: establish and demonstrate a repeatable, safe development workflow before implementing GrowthTwin product features.
- Product direction: an AI-assisted content, review, publishing, and analytics workflow for dental clinics in Türkiye.
- Keep hosted evaluations synthetic and credentials out of chat and Git. No paid infrastructure or staging service without an explicit approved plan.

## Repository and review

- Repository: https://github.com/ugurkbcgl-hub/growthtwin (public; main is the default branch).
- Checkout: C:\Users\Public\Desktop\GrowthTwin, on branch docs/post-pr8-handoff; PR #9 is open with this post-merge handoff refresh.
- PR #3 merged as 394d3d4; post-merge CI passed.
- PR #4 merged as 2f53376; post-merge CI passed with the Django check, Ruff formatting, and Ruff lint.
- PR #5 merged as 580d972; post-merge CI passed with dependency auditing.
- PR #6 merged as 60e3e92; post-merge CI passed with the source and wheel build checks.
- PR #7 merged as e4b5738 on 2026-09-27. Its required CI passed, and post-merge main CI run 36315736901 succeeded, including formatting, lint, dependency audit, distribution content checks, Django system check, migration consistency, and Django tests against PostgreSQL 18.6.
- PR #8 merged as 0b640d5 on 2026-09-27. Required CI run 36316352002 and post-merge main CI run 36316433857 both succeeded.
- main protection requires a PR and the Django system check from GitHub Actions on an up-to-date branch; it also requires linear history and conversation resolution, applies to administrators, and blocks force-push and deletion.
- Use feature branches and PRs. The user has delegated routine project decisions, including merges after review and successful required CI.

## Phase 0 status

- M2 is recorded complete in the roadmap. Local PostgreSQL service state and protected credential storage were not checked in this turn.
- M3 guardrails are complete for the Django shell: architecture/docs, required configuration check, Ruff format/lint, dependency audit, and source/wheel build verification are in main. A type checker remains unselected until the codebase benefits from one.
- M4 synthetic profile-edit demo is merged in PR #7. Four local tests passed using isolated in-memory SQLite settings; CI also passed the behavior tests against ephemeral PostgreSQL 18.6. The build verifies both archives contain the demo templates.
- Staging recommendation: Heroku Basic web dyno + Essential-0 Postgres, about USD 12/month before taxes/optional services; PostgreSQL 18 is currently supported. Render free Postgres expires after 30 days and has no backups. Shutdown means deleting the Heroku app and database after M4 acceptance. Pricing checked 2026-09-27; see ROADMAP.md for official links. No staging service has been enabled; approval of the recurring-cost plan is still required before provisioning.
- Product feature implementation, social publishing, and AI provider calls remain out of scope.

## Next action

Obtain approval for the proposed USD 12/month Heroku staging plan before provisioning. If approved, use synthetic data only, run the Playwright and deployment-safety checks, and delete the app/database after M4 acceptance.

## Not rechecked

- Local PostgreSQL service and the DPAPI-protected credential store.
- NVIDIA Build account quotas and current model limits.
- Whether the owner approves the proposed USD 12/month Heroku staging charge. Pricing and PostgreSQL 18 support checked 2026-09-27; no service was provisioned.
