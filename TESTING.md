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
CI 39649793207 verified both orderings within 393 PostgreSQL tests and 10 browser tests; post-merge main CI 39650308546 passed. Local SQLite cannot prove this row-lock behavior.
Migration 0002 was applied only to ephemeral test DBs, not preserved Google or
browser fixture DBs. No UI changes or new browser test in this service-only slice.
This is not a production restore or already-sent remote-action guarantee.


## Campaign stage overview

`campaigns.test_journey` adds 16 tests. Together with campaigns.tests,
`test_exports` and `test_rehearsal_views`, 63 focused tests passed with no skips.
Coverage includes owner/inactive/foreign/missing access, GET/HEAD no writes,
405 mutations, error privacy headers, current source/version preference,
plan prerequisites, approval existence versus current consent, stored TEST
state allowlisting and existing dispatch priority after source changes.
Projection queries exclude dispatch payloads; provider/grant/verification calls
are patched to fail. Exact loopback owner/workspace/remote/forwarded visibility
and prerequisites are checked. Currency is taken from the stored draft.
Ruff, formatting and migration drift passed; no new migration.

Browser fixture 127.0.0.1:8011 used the preserved isolated closure preview DB,
unusable-password synthetic owner and Google disabled. Created synthetic draft 1,
selected the first current creative and verified the suggested step changed from
creative selection to plan review without inventing approval/dispatch/results.
Plan Enter navigation, report roundtrip and list-to-journey worked. Desktop and
390x844 viewport screenshots were inspected; mobile document/client widths were
375/375 with no horizontal overflow. Viewport reset. Proof outside Git in the
conversation workspace: campaign-journey-desktop.png and campaign-journey-mobile.png.
The helper session is not a product login or staging E2E test. Restart applied
previous migration 0002 only to that isolated fixture DB; actual Google preserved
DB/grant/ledgers and Heroku were untouched. PR #302 required CI 39653009712 passed 409 PostgreSQL tests and 10 browser E2E tests; post-merge main CI 39653441692 passed.


## Protected TEST navigation

`connections.test_draft_navigation` adds 14 tests; together with existing draft
review/dispatch, total-budget, header and campaign journey checks, 55 focused tests pass.
Coverage includes scoped shared links, escaped names, unchanged fixed consent,
CSRF/host/forwarded/owner/method denial, missing/unknown/uncertain/stale state,
metadata-only status GET and no provider/credential/payload/write on that GET.
Owned errors retain links; unresolved approvals do not expose a campaign link.
Mocked validation/operation responses verify result scope, status codes and links;
they are not new Google evidence. Ruff/format/migration drift passed; no migration.

Desktop/mobile browser reviewed the shared review and uncertain-status screens,
expanded the full package, followed status and campaign-back links using Enter,
and reset viewport. Mobile document/client widths375/375 (390x844 override).
Proof outside Git: test-review-navigation-{desktop,mobile}.png and
 test-status-navigation-{desktop,mobile}.png in the conversation workspace.
Helper Temp/growthtwin_test_navigation_preview.py uses the existing validated
isolated fixture DB/cookies with unusable-password synthetic owner; creates only
fixed synthetic draft2/approval/uncertain metadata. A prominent fixture label and
stubbed configuration distinguish it from actual Google evidence. Google flags
remain false; browser used no operation POSTs. Preview-only GET routes render the
inner presentation with a fixed stub; they do not prove product authentication or
local endpoint authorization. Actual protected views/CSRF are exercised in tests.
Preserved Google DB/grant/ledgers, Heroku and real data remain untouched.

Shared result/error documents preserve same-origin referrers for their local logout form CSRF Origin. Callback/start remain no-referrer; external referrers remain suppressed. Existing header test and result assertions passed.

PR303 first PostgreSQL CI39716734298 rejected an overlength synthetic unknown-state fixture (varchar20). The test label was shortened; application/model constraints unchanged. Latest-head CI must pass before merge.
