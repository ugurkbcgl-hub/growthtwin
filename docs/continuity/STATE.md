# GrowthTwin — current handoff

Verified: 2026-10-21 20:50 Europe/Istanbul (+03:00).

## Objective

Türkiye self-service advertising across industries. Local synthetic Google
DAILY/total-budget PAUSED TEST lifecycle works. Real data, production serving
and media spend remain gated.

## Repository

Verified base main 852d60f: PR #299 merged; latest-head required CI 39644787052
and post-merge main CI 39645131181 passed (362 PostgreSQL tests + 10 browser E2E).
No open PR at start. Current branch feat/synthetic-closure-results; bounded fixed
fake STOP result implementation/tests/docs await PR and required CI. Snapshot
precedes its own commit; verify latest head/checks live. Reviewed green PRs may
squash merge under standing owner authorization. Never force merge, disable
checks, push main directly or enable auto-merge.

## Verified Cloud/OAuth observations — read-only

Cloud console observations below were verified October 19, not rechecked today.

- Existing test Cloud project: Ads API Enabled, current access Test, 15,000 daily
  TEST operations. Explorer Apply for access visible, NOT clicked/submitted.
- OAuth External/Testing, one test user of 100. Publish app disabled until Branding
  complete. Home/privacy/terms URLs and authorized domain list empty. Verification
  Center says verification not required because Testing; not production approval.
- All three Data Access scope declaration tables empty. This does not invalidate
  the existing encrypted runtime adwords TEST grant or past TEST proof.
- Owner confirmed no domain yet. No purchase, new project/service, scope change,
  upgrade, publishing action or real advertiser connection occurred.
- docs/product/google-production-access-audit.md separates API access, OAuth
  publication and advertiser/financial readiness, with current official sources.
  Testing grant expiry is generally seven days for these scopes; exact current
  grant expiry was not inspected or calculated. Do not rotate needlessly.
- Requirements now in docs/product/public-identity-page-requirements.md:
  page acceptance criteria, code-derived data inventory, missing owner facts,
  retention/ledger deletion and test/production project separation. Existing
  home route exists; separate contact/privacy/terms routes are now implemented.
- Protected approval/dispatch snapshots include content. Do not promise immediate
  total deletion or delete durable no-resend intent to satisfy a naive cleanup.
- Implementation: static GET/HEAD-only /iletisim/, /gizlilik/ and
  /kullanim-kosullari/, shared links and public home footer. Visible draft labels,
  noindex, no forms/scripts or new data collection on these pages.
- Five focused SimpleTestCase tests passed without DB access, including anonymous
  access, links, method rejection, HEAD, no cookie writes and no query reflection.
  Ruff format/check and git diff --check passed. Desktop/mobile browser navigation,
  focus and layout reviewed; mobile document/client width 375/375, no horizontal
  overflow on info pages or home footer. Independent code review had no findings.
- Separate temporary preview at 127.0.0.1:8010 uses in-memory test DB and its own
  cookie name, not the preserved Google DB. Initial home error from an existing
  browser cookie was resolved by that cookie isolation; home then passed review.
  This preview supports information-page review, not campaign operation.
- ADR-0027 now defines category-specific retention/deletion/recovery boundaries,
  separate stop/revoke/secret/local/recipient/backup outcomes, no-resend barrier
  versus content snapshot, in-flight/callback races and restore quarantine.
  No production mechanism, model, migration, erasure or new duration was added.
  Official Google revoke and KVKK destruction regulation checked on October 19.
  Independent review found one misleading workspace-delete phrase; corrected to
  campaign-draft deletion. No other findings. git diff --check passed; no new
  local application tests run for this documentation-only step.
- Follow-up code: connections/lifecycle_decision.py is a pure frozen/typed
  synthetic evaluator returning eligible closure steps and independent Turkish
  messages. It blocks new work universally; request/recovery/barrier proof gaps,
  in-flight and missing erasure facts fail closed. BLOCKED erasure never becomes
  ERASE_LOCAL automatically; immediate revoke does not suggest stop/reconcile.
- 15 focused SimpleTestCase tests passed without DB access; ruff format/check
  and git diff --check passed. Independent review's BLOCKED-state gap was fixed,
  regression assertion added and reviewer confirmed no remaining findings.
  No DB/API/UI/model/migration changes or credential/ledger operations. Caller
  proof booleans are assertions, not implemented auth/CSRF/durability/freshness.
- Follow-up reducer: lifecycle_observation.py binds synthetic outcome evidence
  to workspace/connection/request/generation, revision and one pending operation
  ticket. Exact replay is a no-op; event-ID content conflicts, wrong identity/
  ticket/revision, closed requests and unverified recovery/barrier are rejected.
  Outcome changes cannot alter safety flags, generation, closed status or grants.
- 14 reducer tests plus 15 decision tests passed (29 DB-free); ruff format/check
  and git diff --check passed. Independent read-only review found no blocking
  issue. Pending tickets/provider evidence are caller assertions; no issuance,
  durable store, atomic CAS, timestamp freshness or runtime auth is implemented.
  No DB/API/UI/migration/credential operations; existing TEST routes unchanged.
- Pure issuance is now in lifecycle_ticket.py: only eligible supported steps
  issue typed source/outcome/revision tickets. Exact issuance replay is a no-op;
  conflicts, retired operation IDs and unresolved normal replacement are rejected.
  Immediate REVOKE may use one separate priority slot, preserving the original
  ticket. Reducer consumes only the matching slot; both result orders tested.
  New safety metadata cannot be future-dated or mismatched with its outcome.
- 13 new issuance tests + prior 29 passed (42 DB-free); ruff format/check and
  git diff --check passed. Independent review found no blocking issue; optional
  reverse-order test was added. Code tree unchanged by dependency rebase.
  Still no storage/executor/provider proof/credential/UI effects. A duplicate
  result never authorizes resending. Fresh observation correlation is not
  implemented provider freshness verification; never re-stamp a stale event.
- October 20 preview: GET/HEAD-only /kontrol-onizleme/ now renders five fixed
  allowlisted scenarios using the three pure contracts; shared public footer
  links it. No account/evidence/text input, forms, scripts, real action buttons
  or session writes. Simulation labels distinguish examples from account state.
- Nine preview + five information + 42 contract tests passed October 20 (56 DB-free),
  including secret-read/token POST guards and ignored extra query inputs. Ruff
  format/check and git diff --check passed. Independent review: no blocking issue.
- Browser verified all scenario navigation, desktop/mobile layout and keyboard
  Tab/Enter, with mobile content/client width 375/375. Temporary viewport reset.
  Separate in-memory preview server restarted on 8010; its own cookie prevents
  borrowing the preserved Google session. Proof outside Git in conversation
  workspace: lifecycle-preview-desktop.png and lifecycle-preview-mobile.png.

## Preserved product evidence

PR #289 browser verified new synthetic draft 2 with 5,000 TRY CUSTOM_PERIOD,
October 20–November 3, exact readback/repeat create/stop. Original draft 1 DAILY
333.33 TRY November 1–15 retained read/stop. 82 targeted tests passed in that
implementation. No production budget exhaustion/aggregate cap proof is implied.

## Current slice — synthetic persistence

- Two new connections tables hold synthetic closure requests/issuance receipts.
  Owner-scoped service create/read/issue/observe only; no HTTP/executor integration.
- Unique workspace/connection request and global operation identity, row locks,
  revision-conditional update and transactional receipt insertion. Creation replay
  returns current progress; no reset/generation replacement/delete API.
- Strict versioned typed codec, revision and exact unique receipt-set validation;
  corrupt/unsupported state fails closed. PROTECT prevents silent owner/workspace
  cascade of these synthetic barriers, not a final lawful deletion implementation.
- 62 focused local tests passed (20 new DB tests + 42 pure contracts); one
  additional PostgreSQL competing-writer test skipped on SQLite, then passed CI
  39642369641 on PostgreSQL before #298 merged.
  Migration drift, ruff and independent re-review passed. Review's creation-conflict
  classification and duplicate-operation/orphan-receipt findings fixed and tested.
- Migration applied only to ephemeral local test DB. No preserved Google DB,
  encrypted grant, immutable ledger, Heroku, provider or credential operations.
  No actual erasure. Initial snapshot flags remain synthetic fixture assertions;
  DB persistence does not make them verified provider facts. The fixture barrier
  is not wired into existing Google routes; no production recovery proof implied.

## Current slice — fixed synthetic owner journey

- Default-off SYNTHETIC_CLOSURE_UI_ENABLED gates /workspace/control/ and the
  campaign-list link. Active authenticated owner only; explicit synthetic-only
  confirmation and CSRF-protected POST start a fixed STOP-pending example.
- Server-derived fixture identities/facts; submitted extra fields/proof/outcomes/
  IDs rejected. Creation+issuance share one transaction; repeated start resumes
  existing progress. GET/HEAD overview/status create no closure or provider work.
- Six separately labeled example outcomes, generic corruption 409, private/no-store
  and noindex headers including errors. No real completion/revoke/erase controls.
- 80 focused local tests passed (18 journey + 20 store + 42 pure); two PostgreSQL
  competing-writer tests skipped on SQLite and await required CI. Ruff/migration
  drift and independent read-only review passed with no blocking findings.
- Browser checked desktop/mobile overview/start/status/reload/resume/campaign link
  and Space/Tab/Enter. No horizontal overflow: overview 375/375, status 390/390.
  Temporary viewport reset. Proof outside Git: closure-journey-start-desktop.png,
  closure-journey-status-desktop.png and closure-journey-status-mobile.png in the
  conversation workspace. No new schema, provider, credential or actual erasure.

## Current slice — explicit fake STOP results

- Two fixed separately stored confirmed/uncertain examples. Existing default IDs
  preserved. Only a deterministic local fake supplies the result, not POST fields.
- Explicit owner/CSRF POST and ten-minute signed owner/workspace/request/operation/
  revision token. Extra evidence, stale/tampered/foreign token or changed state
  rejected. Outer transaction holds scoped row lock through result persistence.
- Exact saved-event replay bypasses fake invocation and adds no operation/event.
  GET/HEAD status read-only, controls disappear on result; six outcomes distinct.
- 94 focused local tests passed; three PostgreSQL-only concurrency tests skipped
  on SQLite and await CI. Ruff, migration drift and independent review passed.
- Browser both outcomes/reload and mobile keyboard Space/Tab/Enter passed; width
  375/375, viewport reset. Proof outside Git: closure-result-confirmed-desktop.png,
  closure-result-uncertain-desktop.png, closure-result-uncertain-mobile.png.
- No real provider, credential, erasure, schema/migration, Heroku or spend changes.
  Stored fixture barrier still does not protect existing Google runtime routes.

## Next action

After reviewed result PR passes required CI and merges, begin accepted plan step 2:
implement a fail-closed new-work/callback guard for isolated synthetic scope and
generation, used only by fake operations. Test closure races and stale callbacks;
inspect actual TEST create/refresh/callback hooks from code before later runtime
mapping. Fixture IDs are not actual Google connections. Preserve Google DB/grants/
ledgers and add no real provider executor, erasure, account, spend or paid service.
Then continue unified advertiser journey and remaining launch gates in ROADMAP.

## Local environment

Preserve LocalAppData/Temp/gwt-oauth-isolated-wq0dp50j/synthetic.sqlite3,
owner/workspace identity, encrypted grant and both durable ledgers. Helper:
LocalAppData/Temp/growthtwin_oauth_preserved.py. Never run the older fresh-DB
bootstrap or reset existing intent. Generated local login is not recorded.
Latest browser draft-dispatch result for draft 2: stopped / PAUSED, 5,000 TRY CUSTOM_PERIOD. Original draft 1 remains stopped / PAUSED, 333.33 TRY DAILY. Preserve both ledgers and all draft IDs.
Status controls: /connections/google/draft-status/?draft=1. Server/helper
availability is ephemeral; verify before use. Grant stored with user-scoped
Windows DPAPI outside Git; reuse it rather than unnecessary reauthorization.
Read-only requirements and implementation reviews completed with no findings;
no agent work remains running. Google DB/grant/ledger unchanged. Preview proof
outside Git: conversation workspace information-contact-desktop.png and
information-mobile-footer.png. Server lifetime is ephemeral.

Current owner-journey browser fixture: 127.0.0.1:8011, session 93512 at this
snapshot. Disposable isolated SQLite under Temp/gwt-closure-ui-preview-*, separate
session/CSRF names, Google features disabled. Helper outside Git:
LocalAppData/Temp/growthtwin_closure_journey_preview.py. Unusable-password synthetic
owner; helper-only /__preview__/ entry creates that fixture session. This is not
product auth or a real sign-in test. Product start/status behavior is exercised
normally after that entry. Do not point this helper at the preserved Google DB;
the helper now reuses only its validated Temp/gwt-closure-ui-preview-28gfu4nv
fixture directory and refuses a usable-password owner. Restart preserved the
synthetic records, not a production recovery proof. Browser tab is
left on saved status. Server availability is ephemeral. No agent remains working.

Latest preview: existing confirmed example now has one saved confirmed STOP event;
new uncertain example has one saved uncertain STOP event. Both revocation/erasure
outcomes remain unverified/pending. Browser tab left on uncertain result.
Accepted plan sequence is now in ROADMAP; only step 1 is implemented in this slice.
