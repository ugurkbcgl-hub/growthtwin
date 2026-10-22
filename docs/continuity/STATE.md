# GrowthTwin — current handoff

Verified: 2026-10-22 07:28 Europe/Istanbul (+03:00).

## Objective and authorization

Türkiye self-service advertising across industries; clinic is only an example.
Normal advertiser journey should need no GrowthTwin staff operator. Develop local
synthetic slices while production gates remain open. Reviewed green PRs may squash
merge under standing owner authorization; never force merge, disable checks,
push main directly or enable auto-merge. No new paid services, real advertiser
connection/data, production publication, media spend or production AI in this slice.

## Repository and CI

Verified base main c91e50a: PR305 merged. Latest-head CI39720686706 passed465
PostgreSQL tests and10 browser E2E tests; main CI39720985597 passed. No open PR
at slice start. Current branch feat/scoped-oauth-candidate-boundary, uncommitted
implementation at this snapshot. New PR/CI not created yet; recheck live state.
PR attachment has hit this chat's100-item limit; attempt once per new PR,
do not remove unrelated attachments. GitHub PRs remain intact.

## Current slice — default-off scoped TEST candidate adapter

- NEW unwired adapter and receipt; normal flag remains False. Separate five-minute
  process-local state/PKCE binding includes owner/workspace/session HMAC and durable
  connector/generation/revision/attempt. No existing route/backend/store change.
- Legacy grant presence denies before client/exchange. EXCHANGING commits before
  transport; callback replay cannot send again. Post-response current scope/time/
  immutable binding recheck precedes a distinct encrypted candidate-only envelope.
- No activation/readback exists. Quarantined identity unchanged; orphan or uncertain
  metadata cannot resume/exchange/revoke automatically. Source adoption/rollback
  plan in ADR0031 preserves old grant/ledgers and separately scoped stop/reconcile.
-20 new local +31 legacy backend/OAuth/store/views tests passed (51 total);2
  PostgreSQL races skip locally and await required CI. Ruff/format/migration drift
  and independent source review passed. All transport/client/path/write/read mocked.
- Migration0005 only applied in ephemeral test DBs. No actual credential, provider,
  candidate file, preserved Google/fixture DB, Heroku or UI action. No browser test.
- These are mocked adapter results, not actual OAuth/Ads target verification,
  active-grant adoption or distributed filesystem/DB recovery proof.

## Verified existing product evidence

- Local Google DAILY/total-budget PAUSED TEST create/read/repeat/stop works.
  Draft 2: 5,000 TRY CUSTOM_PERIOD October 20–November 3. Draft 1: 333.33 TRY
  DAILY November 1–15. Both stopped/PAUSED; no serving/spend/cap-exhaustion proof.
- ADR-0027 pure decisions, observation reducer and ticket issuance are implemented.
  Owner-only /workspace/control/ start/status is default-off; server fixture facts,
  CSRF, owner binding and exact replay preserve one operation per example.
- Two fixed fake STOP outcomes (confirmed/uncertain) are saved through a separate
  explicit signed 10-minute owner/workspace/request/operation/revision POST.
  Existing default IDs retained; revocation/secret/erasure remain independent.
  Browser desktop/mobile/keyboard proof outside Git: closure-result-confirmed-
  desktop.png, closure-result-uncertain-desktop.png and -mobile.png in conversation
  workspace. No real account result is shown by those examples.

## Actual runtime integration gaps — source only

ADR-0027 maps views.local_owner_only/start/callback, google_oauth.begin,
backend.exchange_and_store/disconnect, verification.verify,
test_campaign._access_token/perform and draft_dispatch.perform. Real mapping needs
checks before refresh/exchange/create and again before grant/result acceptance.
backend token identity is owner/workspace, without durable connection UUID or
credential generation; verification fingerprint is not a closure registry.
Fixture UUIDs cannot substitute for actual grant scope. Existing Google routes do
not consume the new guard. Stop/reconcile must stay separately permitted within
verified scope; do not unconditionally disable their needed existing-grant access.
No actual grant, provider, configuration value or DB read in this hook review.

## Open production gates

October 19 Cloud observations (not rechecked today): Test API access, OAuth
External/Testing, one test user; Branding/publish and home/privacy/terms/domain
incomplete. Owner reported no domain then. No upgrade, publish, purchase, new
scope or real account action. Exact current grant expiry was not inspected.
Domain/business/contact, real data recipients/retention/legal review, production
vault/tenant identity, fresh provider evidence, durable restore barriers, configured
DB recovery, current campaign staging E2E and schema rollback remain open. Real
metrics, commercial credit/payment/refund terms and enforceable campaign/aggregate
financial consent/caps must be resolved before real publishing.

## Next action

Finish this reviewed candidate PR/required CI/merge and verify main CI. Then
add strict versioned candidate-envelope validation/readback against its receipt,
current scope and explicit reconciliation dispositions using mocks; no activation
or actual file access while preparing it. Before actual hook rollout, session/
CSRF endpoint wiring, configured TEST target proof, pending/recovery/orphan handling,
explicit legacy adoption/rollback and scoped refresh/stop/reconcile remain open.
Never read/migrate/reactivate/reset the preserved grant implicitly; production
privacy/access/recovery/financial gates remain open.

## Preserved local environments

- Preserve LocalAppData/Temp/gwt-oauth-isolated-wq0dp50j/synthetic.sqlite3,
  owner/workspace identity, encrypted grant and both immutable dispatch ledgers.
  Use helper LocalAppData/Temp/growthtwin_oauth_preserved.py, never the older
  fresh-DB bootstrap. Do not reset ledgers or reauthorize needlessly. DPAPI secrets
  are outside Git under LocalAppData/GrowthTwinsecrets; do not read/print values.
- Browser fixture 127.0.0.1:8011 (session41181 at last check) uses the validated
  Temp/gwt-closure-ui-preview-28gfu4nv/fixture.sqlite3, isolated cookies and
  unusable-password owner. Google flags remain false. Current helper:
  Temp/growthtwin_test_navigation_preview.py; /__preview__/ creates fixture session,
  /__preview__/test-review/ and /test-status/ show explicit fixed examples with a
  stubbed configuration, inner presentation only, no operation POSTs. Draft1 and
  closure examples retained; draft2 is a fixed synthetic approved/uncertain example.
  These records are not actual Google evidence. No new migration in current slice.
  Original helper growthtwin_closure_journey_preview.py still exists. Runtime is
  ephemeral; no agent remains working. Never include secrets in handoff/source.
