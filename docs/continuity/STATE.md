# GrowthTwin — current handoff

Verified: 2026-10-22 06:49 Europe/Istanbul (+03:00).

## Objective and authorization

Türkiye self-service advertising across industries; clinic is only an example.
Normal advertiser journey should need no GrowthTwin staff operator. Develop local
synthetic slices while production gates remain open. Reviewed green PRs may squash
merge under standing owner authorization; never force merge, disable checks,
push main directly or enable auto-merge. No new paid services, real advertiser
connection/data, production publication, media spend or production AI in this slice.

## Repository and CI

Verified base main1419425: PR303 merged. Latest-head required CI39716957472
passed423 PostgreSQL tests and10 browser E2E tests; post-merge main CI39717264957
passed. No open PR at slice start. Its earlier overlength fixture error was fixed.
Current branch feat/connector-identity-generations; uncommitted implementation at
this snapshot, no new PR/CI yet. Recheck live branch/worktree/head/checks.
PR attachment has hit this chat's100-item limit; attempt once per new PR,
do not remove unrelated attachments. GitHub PRs remain intact.

## Current slice — durable connector identity/generation metadata

- Separate ConnectorIdentity/ConnectorGeneration, one google_ads_test slot per
  owned workspace. Server-generated connection/current generation UUIDs with
  ordinal/revision and permanent typed request/generation history. No secrets.
- Initial quarantine, irreversible block, no OPEN/activate/reopen API. Metadata
  rotation never refreshes credentials or implies permission. Exact replay returns
  current metadata even after later rotation/block; stale/conflicting requests deny.
- All paths check active ownership, lock workspace then connection and verify
  history; atomic receipts/CAS preserve consistency. No actual runtime consumer.
-15 new local tests +14 work-guard tests passed (29 total); four PostgreSQL races
  skipped locally, including two new registration/rotation races. Required CI must
  pass those. Ruff/format/migration drift and independent source review passed.
- Migration0003 applied only to ephemeral test DBs. Preserved Google/fixture DBs,
  grants, ledgers, Heroku and UI unchanged. No browser test for service-only slice.
- ADR0029 records the contract and limits. No OAuth handshake or actual credential
  generation mapping, provider request, restore barrier or remote execution proof.

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

Finish the reviewed identity PR/required CI/merge and verify main CI. Then add
a closed-by-default, generation-bound authorization-attempt receipt/result
coordinator with deterministic local fake outcomes. Do not read, migrate,
reactivate or reset the preserved Google grant. Actual OAuth hook integration,
separately allowed stop/reconcile and production identity/privacy/access/recovery/
financial gates remain open; fixture IDs and registry metadata prove no real scope.

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
