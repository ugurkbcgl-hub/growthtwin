# Testing strategy

Keep verification proportional to the change. Local product prototypes use synthetic data and must make mock actions/results visible as mock. Do not contact a publishing platform or trigger ad spend in ordinary tests.

## Current CI and demo coverage

- `.github/workflows/ci.yml` runs for pull requests and pushes to `main`. It installs the Django app and pinned development tools on Python 3.13, checks formatting with Ruff, runs lint, audits installed dependencies with `pip-audit`, builds source/wheel distributions, verifies required templates and static assets are present, runs `python manage.py check`, checks migration consistency, and runs Django tests.
- CI uses an ephemeral PostgreSQL 18.6 service with CI-only placeholder credentials. GitHub destroys the service after the run.
- Pinned Playwright/Chromium browser tests cover the synthetic profile-edit demo and authenticated campaign workspace against that CI PostgreSQL service. Campaign coverage includes owner boundaries, creative editing/version history/restoration, live bounded character counters, and narrow-screen overflow. For focused local runs, use the isolated in-memory SQLite settings and regenerate the static manifest after adding static assets. All product examples stay synthetic; no publisher or spend action is called.
- Dependency auditing requires network access to its vulnerability service. Build artifacts under `apps/web/build/` and `apps/web/dist/` are ignored by Git.
- The protected `main` branch requires the `Django system check` from GitHub Actions and an up-to-date PR branch.

## Product verification layers

Synthetic workspace rehearsal coverage checks owner isolation, POST/CSRF,
start/failure/retry/stop, stale input fingerprints, repeated form revisions,
terminal stop and cascading cleanup. A PostgreSQL-only concurrent duplicate
start test exercises separate connections against the draft row lock in CI;
local SQLite skips it. Browser coverage exercises failure, recovery, stop,
new start and event history at narrow/desktop widths. The fake channel performs
no network calls, produces no real metrics and incurs no spend.

1. **Unit:** campaign states, advertiser authorization, budgets, content validation, and transition rules.
2. **Integration:** PostgreSQL constraints and tenant isolation; AI schema and provider contracts with fakes; platform authorization, idempotency, retries, and result reconciliation with sandbox accounts or controlled fakes.
3. **End-to-end:** brief → campaign preview → configured automation state → report. Until a real destination is selected, publishing/results are synthetic and clearly labeled.
4. **Operational:** readiness and deployed revision, secrets/config separation, backups and restore, rollback, emergency stop, and visible job failures.
5. **Usability/accessibility:** keyboard and screen-reader essentials, responsive layouts, clear progress/error states, short intake effort, and comprehension of limits/results.

## Synthetic closure journey

`SYNTHETIC_CLOSURE_UI_ENABLED` is disabled by default. Enable it only in an
isolated synthetic environment with current migrations and a synthetic owner/
workspace; do not enable it against the preserved Google test DB or real data.
The campaign list then links to `/workspace/control/`. GET/HEAD overview/status
are read-only. Only an explicit owner POST with CSRF and the synthetic-only
confirmation starts the fixed example. No outcome/proof/connection input is
accepted. One example/operation is retained per workspace; refresh/replay does
not reset it. Status remains pending because there is no provider executor.

Focused tests: `growthtwin.modules.connections.test_lifecycle_journey`, plus
the store/decision/observation/ticket modules. On October 21, 80 local tests
passed; two PostgreSQL-only competing-writer tests were skipped on SQLite.
Required CI must verify those on its ephemeral PostgreSQL service. Tests cover
owner/active-state isolation, method/CSRF/confirmation boundaries, extra-field
rejection, no-store error responses, replay, transaction rollback and corrupted
state. Separate browser review checked desktop/mobile/keyboard and resume using
a disposable fixture DB, separate cookie names and an unusable-password owner.
The helper-only fixture session is not a product authentication bypass or a
real sign-in test. Preserved Google DB/grants/ledgers were not used.

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

## Fixed fake closure results

Two fixed examples now demonstrate confirmed and uncertain STOP with distinct
server-owned identities. Result POST requires explicit synthetic confirmation,
CSRF and a ten-minute owner/workspace/request/operation/revision signed token.
`test_lifecycle_results` adds 14 local tests and one PostgreSQL-only concurrent
result race. The focused lifecycle selection has 94 passed locally and three
PostgreSQL-only skips. Exact replay must bypass the fake adapter; expired, stale,
wrong-owner/scope, altered-state or injected outcome/proof requests must not write.
No remote exactly-once/recovery guarantee follows from this deterministic fake.
Desktop/mobile browser checks exercised both results, reload and keyboard action;
the normal viewport was restored. No actual Google/credential/erasure operation.

## Synthetic connection/work ordering

`test_lifecycle_work_guard` adds 14 local tests and two PostgreSQL-only orderings
for closure intake versus a fixed fake work/callback. The focused lifecycle set
has 108 local passes and five PostgreSQL skips. New scope registration is internal,
fixture-only and explicit; default/missing/quarantined/generation-mismatched or
closed scope must deny. The same owned workspace row lock orders closure intake
and local fake execution; rollback must restore both request and scope state.
No arbitrary executor, remote request or actual grant write is accepted. Required
CI must verify both orderings; local SQLite cannot prove this row-lock behavior.
Migration 0002 was applied only to ephemeral test DBs, not preserved Google or
browser fixture DBs. No UI changes or new browser test in this service-only slice.
This is not a production restore or already-sent remote-action guarantee.
