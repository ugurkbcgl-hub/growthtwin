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

PR303 first PostgreSQL CI39716734298 rejected an overlength synthetic unknown-state fixture (varchar20). The test label was shortened; application/model constraints unchanged. Corrected latest-head CI39716957472 passed423 PostgreSQL tests and10 browser E2E tests; PR303 merged and main CI39717264957 passed.


## Durable connector identity metadata

`connections.test_connector_identity` adds15 local tests and2 PostgreSQL-only
races. Together with existing `test_lifecycle_work_guard`,29 local tests pass
and4 PostgreSQL races skip on SQLite. PR304 required CI39719120618 verified all four races in440 PostgreSQL tests and10 browser E2E tests; main CI39719367350 passed.
Registration replay, workspace/owner isolation, stale generation/revision,
retired-generation/request reuse, permanently blocked state, replay after later
rotation/block, corrupt history, receipt rollback and database state/provider
constraints are covered. Reads/writes cannot call provider/credential adapters.
New races check simultaneous registration yields one identity/receipt and two
competing rotations admit only one current generation. SQLite is not lock proof.

Ruff/format/migration drift and independent read-only review passed. Migration0003
was applied only during ephemeral local test DB setup, never to the preserved
Google DB or the browser fixture. No UI/browser run for this service-only slice.
No runtime consumer, credential metadata mapping, actual OAuth handshake, remote
exactly-once, stop/revocation or independent restore-barrier guarantee is implied.


## Default-off synthetic authorization attempts

`test_synthetic_authorization` adds23 local tests and2 PostgreSQL races. With
`test_connector_identity`,38 tests pass locally and4 PostgreSQL tests skip.
PR305 required CI39720686706 verified the four pending races in465 PostgreSQL tests and10 browser E2E tests; main CI39720985597 passed. New races require PostgreSQL: a second perform during a running fake must not
execute twice; a block must commit while fake waits and reject its late success.
Other tests cover default/confirmation, scoped generation/revision, expiry before/
during fake, switch/block/rotation while fake runs, stale active replacement,
historical GET without writes, owner/inactive isolation, missing receipt, caller
transaction rejection, provider/credential adapter isolation and immutable-binding
corruption. Accepted metadata must be ALLOW with aware completion within lifetime;
contradictory fake outcome or corrupt accepted metadata cannot replay as success.

Review finding about accepted metadata consistency was fixed and independently
rechecked. Ruff/format/migration drift passed. Migration0004 ran only in ephemeral
test DBs; no preserved Google/fixture DB, credentials, provider, Heroku or UI use.
No browser check for this service-only slice. A running fake is never resumed or
re-executed automatically; an expired/stale active example may be retired before
a new explicitly confirmed example. This is not real OAuth callback verification,
authorization, grant storage, remote exactly-once or independent restore evidence.


## Scoped TEST candidate boundary

`test_scoped_oauth_candidate` adds20 local tests and2 PostgreSQL races. With
existing `test_backend`, `connections.tests` and `test_views`,51 local tests pass
and2 PostgreSQL tests skip. Every client, token-path check, transport, encrypted
write and read is mocked; only fabricated fixtures are used. No actual grant,
client, endpoint or candidate file is accessed. Tests check default-off, legacy
preservation, one exchange per callback receipt, session/state/client binding,
pre/post scope and lifetime, candidate-only schema/path, inactive permission,
transport/write uncertainty, simulated DB failure after possible file write,
late legacy-file presence, immutable binding and no automatic retry/revoke.

PostgreSQL races remove the process lock to exercise durable parallel-callback
reservation, and block the connector while mocked transport waits to prove no
candidate storage follows. Required CI must verify them. Ruff/format/migration
drift and independent source review passed. Migration0005 only ran in ephemeral
test DBs. No browser test or actual filesystem write/decrypt/Google operation.
The mocked orphan test is not real filesystem/DB distributed recovery proof.

PR306 required CI39722697389 and main CI39722996360 subsequently passed487
PostgreSQL tests and10 browser E2E tests, including its two races.

## Candidate envelope and advisory readback

`test_candidate_readback` adds21 local tests and1 PostgreSQL race. Focused with
`test_scoped_oauth_candidate` and `test_backend`:55 local passes and3 PostgreSQL
skips. All client/transport/path/encrypted I/O is mocked. Strict fields/version/
scope/token bounds, wrong owner/workspace/session, default-off/caller transaction,
corrupt receipts, no activation/write, pending/rejected/uncertain dispositions,
legacy/client changes, malformed/missing storage and post-read scope/binding
changes are covered. The PostgreSQL race allows a concurrent block to commit
during read and denies a match afterward. No actual decrypt/file/provider action,
new migration, browser test or recovery certification. See ADR0032.

PR307 required CI39747787250 and main CI39748174729 subsequently passed509
PostgreSQL tests and10 browser E2E tests, including all three candidate races.

## Synthetic authorization session journey

`test_authorization_journey` adds17 endpoint tests. With
`test_synthetic_authorization`:40 local passes,2 PostgreSQL skips. Coverage includes
double default-off, owner/session/CSRF, signed action/scope/expiry, exact form
shape, replay, blocked/expired/running state, no GET work and framework-error
private/no-store/noindex headers. Real backend/candidate/readback calls are
forbidden by mocks. No new migration or actual credential/provider/preserved DB operation.
`e2e.test_connector_rehearsal` passed locally: desktop/mobile/keyboard, both fake
outcomes, refresh and quarantine preservation; screenshots reviewed outside Git.
Local Playwright1.63.0 (existing dev pin) was installed in the development venv;
no dependency manifest changed. See ADR0033 for session/recovery limits.


## Recovery dispositions

Connection recovery dispositions (2026-10-22): owned metadata-only assessment separates callback wait/restart review, uncertainty reconciliation, inactive review and rejected history; scope/session flags never permit retry or activation. Synthetic-only signed CSRF recovery reopens an existing fixed example in a new owner session by changing only its session marker. Receipt expiry/scope/scenario are bound; no begin/perform, new receipt or deadline extension. Run guards deny stale/expired/running/terminal execution.18 new tests plus17 prior journey tests:35 local passes; extended isolated browser and mobile visual check passed. No migration or actual credentials/provider/preserved DB/Heroku operation. See ADR0034. PR308 required CI39752232154 and main CI39752610827 passed527 tests and11 browser tests. Next: explicit RESERVED-only retirement with generation fencing in mocks; uncertainty cannot be retired/retried automatically.


## RESERVED candidate retirement

Reserved candidate retirement (2026-10-22): default-off unwired owned service requires explicit typed confirmation and current quarantined RESERVED scope. Generation rotation and original REJECTED/retired_before_exchange receipt commit together; unique retirement request and replacement-generation metadata are validated against permanent history. Exact replay returns current identity even after later rotate/block. All non-reserved/stale/blocked or other unresolved history denies. No I/O, cleanup, retry, activation or change to legacy grant/stop/reconcile.14 new local tests plus2 PostgreSQL races; with existing adapter/recovery:42 local passes,4 PostgreSQL skips pending CI. Independent final review passed. Migration0006 only in ephemeral test DBs; no actual credential/provider/preserved DB/UI/Heroku operation. See ADR0035. PR309 required CI39756480228 and main CI39756903416 passed545 tests and11 browser tests. Next: separately reviewed scoped endpoint/session/CSRF wiring with mocked transport, normal runtime off.
PostgreSQL races cover both winners: exchange-first denies retirement; retirement-first seals callback with zero transport. Local rollback test injects failure after rotation and verifies both metadata changes roll back. No manual browser check for this service-only slice.


## Closed scoped candidate endpoints

Closed scoped TEST endpoints (2026-10-22): separate overview/start/callback/retire routes bind signed5-minute forms to configured owner/workspace/session and immutable scope. Both endpoint/candidate flags remain False plus exact loopback/DEBUG/no-forward guards. Separate scoped redirect leaves legacy default/runtime unchanged. State digest marker rejects old/wrong callback before consuming current handshake; allowed callback always303-cleans URL. Retirement digest rechecked under service locks after independent review found a check/use race.25 new tests plus existing adapter/retirement/legacy:76 local passes,4 PostgreSQL skips; independent final review approved. No new migration or actual provider/credential/preserved DB/Heroku operation; no manual browser check. See ADR0036. PR311 required CI39765174203 and main CI39765596754 passed586 PostgreSQL tests and11 browser E2E tests. Follow-up readiness audit: the owner-approved scoped redirect was registered and both old/new URIs re-read; API remains Test and OAuth External/Testing. Current customer.test_account and isolated runtime binding remain unverified. See [October 22 audit](docs/product/google-production-access-audit.md#scoped-test-hazırlığı--22-ekim-2026). Next: complete isolated candidate-exercise prerequisites with the legacy grant/ledgers preserved; flags remain off, no OAuth/refresh/adoption/publish/cleanup.


## Isolated closed preparation — 2026-10-22

No application code changed or local automated test suite run. A new temp SQLite
DB was migrated and checked for a distinct explicit owner/workspace pair,
unusable-password owner, quarantined connector and zero candidate/Google ledger
rows. Credential/client/transport functions were denied in the preparation process;
no server/provider/credential I/O occurred. No existing DB was opened. This is
bootstrap evidence only, not concurrency, browser authentication, callback log
safety, TEST-target or actual OAuth evidence. See [preparation record](docs/product/scoped-test-exercise-preparation.md).
Baseline PR312 required CI39768028595 and main CI39768447961 passed586 PostgreSQL
tests and11 browser E2E tests. Follow-up documentation CI must be verified separately.
