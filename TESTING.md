# Testing strategy

Keep verification proportional to the change. Local product prototypes use synthetic data and must make mock actions/results visible as mock. Do not contact a publishing platform or trigger ad spend in ordinary tests.

## Current CI and demo coverage

- `.github/workflows/ci.yml` runs for pull requests and pushes to `main`. It installs the Django app and pinned development tools on Python 3.13, checks formatting with Ruff, runs lint, audits installed dependencies with `pip-audit`, builds source/wheel distributions, verifies required templates and static assets are present, runs `python manage.py check`, checks migration consistency, and runs Django tests.
- CI uses an ephemeral PostgreSQL 18.6 service with CI-only placeholder credentials. GitHub destroys the service after the run.
- Pinned Playwright/Chromium browser tests cover the synthetic profile-edit demo and authenticated campaign workspace against that CI PostgreSQL service. Campaign coverage includes owner boundaries, creative editing/version history, live bounded character counters, and narrow-screen overflow. For focused local runs, use the isolated in-memory SQLite settings and regenerate the static manifest after adding static assets. All product examples stay synthetic; no publisher or spend action is called.
- Dependency auditing requires network access to its vulnerability service. Build artifacts under `apps/web/build/` and `apps/web/dist/` are ignored by Git.
- The protected `main` branch requires the `Django system check` from GitHub Actions and an up-to-date PR branch.

## Product verification layers

1. **Unit:** campaign states, advertiser authorization, budgets, content validation, and transition rules.
2. **Integration:** PostgreSQL constraints and tenant isolation; AI schema and provider contracts with fakes; platform authorization, idempotency, retries, and result reconciliation with sandbox accounts or controlled fakes.
3. **End-to-end:** brief → campaign preview → configured automation state → report. Until a real destination is selected, publishing/results are synthetic and clearly labeled.
4. **Operational:** readiness and deployed revision, secrets/config separation, backups and restore, rollback, emergency stop, and visible job failures.
5. **Usability/accessibility:** keyboard and screen-reader essentials, responsive layouts, clear progress/error states, short intake effort, and comprehension of limits/results.

## AI evaluation

- Keep model quality/latency experiments separate from application correctness tests.
- Use a small, versioned synthetic benchmark covering representative advertiser types and the first chosen campaign/channel tasks.
- Score factuality against known brand facts, policy/claim handling, destination-format validity, schema validity, useful draft quality, latency, cost, and failure behavior. A single sample is not evidence of reliability.
- Existing Qwen/NVIDIA dental-task measurements in `AI_PROVIDERS.md` are exploratory, one-run results. They do not prove quality across customer types and do not authorize autonomous publishing.
- Record provider, model identifier, date, latency, failures, and observed quota; never record keys or real advertiser data. Trial hosted services are not production acceptance tests.

## Phase gates

- Local website and campaign UX can be tested with synthetic data before staging/recovery work is complete.
- Before real platform accounts, an external beta, or production, verify staging E2E, backup/restore, rollback, controlled CI failure blocking, platform permission revocation, spend ceilings, stop behavior, and the main advertiser journey. Record actual results; do not infer them from CI's synthetic test.
- Never use staging or a hosted trial model for real advertiser/customer data or live paid campaigns.
