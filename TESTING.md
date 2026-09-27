# Testing strategy

Status: Phase 0 policy. Add automated checks alongside a chosen implementation stack; do not add framework-specific tooling before that choice. Keep verification proportional to the change and focus on the critical user and operational paths.

## Before product features

- Review documentation and architecture changes for consistency, secret leakage, and scope drift.
- For repository changes, run only checks supported by the current repository. Keep Phase 0 demo tests synthetic and separate from product acceptance coverage.
- CI checks formatting, linting, dependency vulnerabilities, Python distribution builds, Django configuration, migration consistency, and focused demo behavior. Add type checks and broader tests as the application grows.

## Current CI baseline

- `.github/workflows/ci.yml` runs for every pull request and for pushes to `main`, including documentation-only changes. It installs the Django application in editable mode with pinned development tooling on Python 3.13, checks formatting with `python -m ruff format --check .`, lints with `python -m ruff check .`, audits the installed Python dependencies with `python -m pip_audit --local --skip-editable --progress-spinner off`, builds source and wheel distributions with `python -m build --sdist --wheel`, and runs `python manage.py check` with non-secret placeholder settings.
- These are formatting, static lint, dependency vulnerability, package build, and configuration/system checks. The current tests cover only the synthetic profile-edit demo. They do not exercise product workflows or external integrations. The dependency audit needs network access to query the vulnerability service. The build creates distribution artifacts under `apps/web/build/` and `apps/web/dist/`; Git ignores both paths.
- The distribution verifier checks that both archive formats include the login and profile templates.
- The job starts an ephemeral PostgreSQL 18.6 service with CI-only placeholder credentials, verifies migration consistency, and runs the Django test suite. GitHub destroys the service when the job ends. Local focused tests can use config.test_settings to run on an in-memory SQLite database without touching the restricted development database.
- Branch protection requires the passing `Django system check` status from the GitHub Actions app and requires the PR branch to be up to date with `main`.

## Product verification layers

1. **Unit:** domain rules such as workspace authorization, content versioning, and approval invalidation.
2. **Integration:** persistence constraints, tenant isolation, job idempotency, and provider adapter contracts using fakes or sandbox accounts.
3. **End-to-end:** the critical path from editing a profile/content draft through approval and the relevant status screen. Publishing tests must use a sandbox or a controlled fake until explicitly authorized.
4. **Operational:** readiness/health behavior, deploy version visibility, backup restoration, and rollback.

## AI evaluation

- Keep model quality/latency experiments separate from application correctness tests.
- Use a small, versioned, synthetic evaluation set. Review output quality against task-specific criteria; do not treat a single sample as proof of quality.
- Record provider, model identifier, date, latency, failures, and any quota observed, but never record API keys or real customer data.
- Do not run broad or repeated model sweeps without a concrete decision they will inform. Hosted trials are not production acceptance tests.

## Phase 0 acceptance checks

M4 should verify the synthetic demo profile-edit path, `GET /health/` database readiness and deployment version, backup/restore, and rollback. M5 should exercise a CI failure that blocks merge and a controlled rollback. Record actual commands, outcomes, and costs in the completion report.
