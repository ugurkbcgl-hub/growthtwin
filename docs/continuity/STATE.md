# GrowthTwin — current handoff

Last verified: 2026-09-27 15:16 (Europe/Istanbul)

## Goal and working rules

- Complete Phase 0: establish and demonstrate a repeatable, safe development workflow before implementing GrowthTwin product features.
- Product direction: an AI-assisted content, review, publishing, and analytics workflow for dental clinics in Türkiye.
- Keep hosted evaluations synthetic and credentials out of chat and Git. No paid infrastructure or staging service beyond the explicitly approved Heroku plan.

## Repository and review

- Repository: https://github.com/ugurkbcgl-hub/growthtwin (public; `main` is the default branch).
- Checkout: `C:\Users\Public\Desktop\GrowthTwin`, on `m4/heroku-staging`, based on `main` at `76c4527`.
- PR #9 was merged as `76c4527` on 2026-09-27. Its required `Django system check` passed (run `36316593684`); post-merge `main` CI run `36316666985` also passed.
- No PR is open for the current staging work yet. The branch currently contains uncommitted Heroku runtime, security, readiness, CI, ADR, and continuity updates.
- Main protection requires PR review flow, the passing `Django system check` on an up-to-date branch, conversation resolution, and linear history; force-push and deletion are blocked.
- The owner delegated routine implementation and merge decisions after review and successful required CI.

## Phase 0 status

- M2 is recorded complete. Local PostgreSQL service state and DPAPI-protected credential storage were not rechecked in this session.
- M3 guardrails are complete for the Django shell.
- M4 synthetic profile-edit demo is merged in PR #7. The approved staging plan is one Heroku Basic dyno and one Essential-0 PostgreSQL 18 database at about USD 12/month before taxes. No Heroku app or database exists yet.
- The owner approved this bounded staging spend on 2026-09-27. No paid add-ons or additional dynos are authorized; delete the app and database after M4 acceptance. Use synthetic data only.
- Heroku onboarding is not complete: the in-app browser currently displays the Terms of Service page, the Heroku CLI is not installed, and no authenticated deployment session is available. No terms were accepted or cloud resources created by Codex.
- Current branch adds the root Heroku Python entry point and dependencies, Gunicorn/WhiteNoise/DATABASE_URL settings, HTTPS and secure-cookie/HSTS configuration, a GET-only database readiness endpoint, focused tests, CI validation, and ADR/deployment documentation.
- Local checks completed: Ruff format/lint; pip-audit (no known vulnerabilities); source/wheel build and template archive checks; Django `check --deploy`; WhiteNoise `collectstatic`; migration consistency; six Django tests using isolated SQLite settings; synthetic `DATABASE_URL` parsing with SSL required. The deployment check exits successfully with Django advisories W005/W021 because HSTS is intentionally not extended to subdomains or preload. PostgreSQL CI for this new branch has not run yet.
- Product features, social publishing, and AI provider calls remain out of scope.

## Next action

Review the current diff, commit and push `m4/heroku-staging`, open its PR, and wait for the required CI result. After the reviewed change is merged, the owner must complete Heroku's Terms of Service and sign in through the browser before the approved resources can be provisioned.

## Not rechecked

- Local PostgreSQL service and DPAPI-protected credential store.
- NVIDIA Build account quotas and current model limits.
- Heroku account setup and authentication. No app, database, dyno, or add-on has been created.
