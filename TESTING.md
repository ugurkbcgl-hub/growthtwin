# Testing strategy

Status: Phase 0 policy. Add automated checks alongside a chosen implementation stack; do not add framework-specific tooling before that choice. Keep verification proportional to the change and focus on the critical user and operational paths.

## Before product features

- Review documentation and architecture changes for consistency, secret leakage, and scope drift.
- For repository changes, run only checks supported by the current repository. Do not claim an app test passed when there is no app yet.
- CI should eventually check formatting, lint, types, unit/integration tests, dependency/security signals, and build output after the stack is chosen.

## Current CI baseline

- `.github/workflows/ci.yml` runs for every pull request and for pushes to `main`, including documentation-only changes. It installs the Django application's declared dependencies on Python 3.13 and runs `python manage.py check` with non-secret placeholder settings.
- This is a configuration/system check only. The Phase 0 shell has no product test suite, and this workflow does not exercise database-backed behavior or PostgreSQL integration.

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

M4 should verify the synthetic demo profile-edit path, application health/readiness, deployment version, backup/restore, and rollback. M5 should exercise a CI failure that blocks merge and a controlled rollback. Record actual commands, outcomes, and costs in the completion report.
