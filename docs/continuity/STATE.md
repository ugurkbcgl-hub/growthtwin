# GrowthTwin — current handoff

Verified: 2026-10-19 20:05 Europe/Istanbul (+03:00).

## Objective

Türkiye self-service advertising across industries. Local synthetic Google
DAILY/total-budget PAUSED TEST lifecycle works. Real data, production serving
and media spend remain gated.

## Repository

Main b06398c: PR #292 merged after required CI 39287123904 passed; #293 merged
after required CI 39290073430 passed. Previous main 4d3d94f CI 39290018147 passed;
current main CI 39290944848 is in progress. PR #294 now targets main, rebased
head 93649e6, CI 39290998289 in progress. PR #295 rebased onto #294, head
66eb69c, CI 39291003701 in progress. Current branch feat/lifecycle-ticket-issuance
builds on #295, implementation head 69e5fd1. This snapshot precedes its own PR.
Verify heads/bases/checks; merge in
dependency order, retargeting/rebasing the child when its parent is squash merged.
Reviewed green PRs may merge under standing owner authorization.

## Verified Cloud/OAuth observations — read-only

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

## Preserved product evidence

PR #289 browser verified new synthetic draft 2 with 5,000 TRY CUSTOM_PERIOD,
October 20–November 3, exact readback/repeat create/stop. Original draft 1 DAILY
333.33 TRY November 1–15 retained read/stop. 82 targeted tests passed in that
implementation. No production budget exhaustion/aggregate cap proof is implied.

## CI observation at this snapshot

PR #290 latest-head run 39278829487 is now confirmed success and #290 merged.
PR #291–293 merged; rebased #294–295 latest heads await CI completion. Auto-merge is not enabled; linear
history rules also reject merge commits, so use squash after checks pass.
No repository rule was changed. Do not force merge or disable checks.
Merge reviewed PRs in dependency order only when their own required checks pass.

## Next action

Settle dependent PRs in order after required CI; then add a read-only local
lifecycle preview using fixed synthetic scenarios from these contracts, with
clear simulation labels and no real closure/revoke/delete buttons or submitted
personal data. Do not wire an executor or access preserved Google DB/grants.
Suggestions/tickets are not runtime authorization; persistence/concurrency/
provider freshness proof remains open.
Domain/business/contact, real recipients, retention periods and qualified review
remain open before final public text/production. Preserve TEST setup, immutable
existing ledgers and encrypted grant; no upgrade, publish, scope grant, purchase
or real advertiser/spend action now.

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
