# GrowthTwin — current handoff

Verified: 2026-10-22 17:02 Europe/Istanbul (+03:00).

## Objective and authorization

Türkiye self-service advertising across industries; clinic is only an example.
Normal advertiser journey should need no GrowthTwin staff operator. Develop local
synthetic slices while production gates remain open. Reviewed green PRs may squash
merge under standing owner authorization; never force merge, disable checks,
push main directly or enable auto-merge. No new paid services, real advertiser
connection/data, production publication, media spend or production AI in this slice.

## Repository and CI

Verified main0c87014: PR312 merged. Required CI39768028595 and main CI39768447961
passed586 PostgreSQL tests and11 browser E2E tests. No open PR at slice start;
main clean. Current branch docs/isolated-scoped-preparation; documentation-only
follow-up before its own PR/CI. Verify live head/checks. PR attachment has a
known100-item limit; remove no unrelated attachments.

## Preserved configuration readiness — earlier October22 audit

- Owner explicitly approved only the new local scoped callback on GrowthTwin
  Web Test. Saved/reopened client contains both original /google/callback/ and
  new /google/scoped/callback/ at http://127.0.0.1:8002/connections.
- Cloud rechecked today: Ads API Enabled/Test; OAuth External/Testing, one test
  user; Branding URLs/domains empty. No upgrade/publish/scope/credential change.
- Ads UI manager/child IDs match preserved helper source constants, not verified
  current process/owner/workspace binding. Three campaigns; paused/no-serving
  warning and zero displayed clicks/impressions/cost for October16–22 only.
- Current customer.test_account=True not re-queried. No grant refresh, OAuth
  exercise, candidate activation/adoption, campaign action or ledger SQL read.
  Helper inspected as AST only because executing it changes DB/user state.
  No credential read, preserved DB migration, Heroku or runtime flag change.
- Both scoped flags remain False. Same-process PKCE, proxy/access/error logging,
  isolated identity/client/target binding and uncertain-outcome reconciliation
  must be established before any separately authorized actual candidate exercise.
  No local tests run for this documentation/configuration slice; code unchanged.
  See docs/product/google-production-access-audit.md, October22 follow-up.

## Current slice — closed isolated preparation

- Fresh DB only: %TEMP%\gwt-scoped-preparation-_jafwrsl\synthetic.sqlite3.
  Private preparation.json holds owner/workspace PKs and connector/generation IDs.
  Both numeric PKs explicitly random/large; no default1/1 legacy-path collision.
- Migrated only new DB, unusable-password synthetic owner/workspace, quarantined
  connector. Zero attempts and Google ledgers; corresponding legacy path absent.
  New actual candidate path cannot be checked until exact attempt exists.
- Git-external helper %TEMP%\growthtwin_prepare_closed_scoped.py denies credential
  read/write, client load and transport functions. No provider/credential I/O,
  server, session, OAuth, refresh or preserved DB/grant/ledger access. Normal scoped
  flags False; preparation process also local OAuth/campaign False.
- Helper creates a NEW environment if rerun; not a resume/reset mechanism.
  Temp files may disappear. Do not bypass unresolved history with new identities.
  Existing fixed TEST client not loaded; new DB does NOT mean separate client.
- Independent source/new-DB read-only review passed. I/O declarations are source
  observations, not instrumented counters/general egress protection; runtime must
  re-establish this DB/identity/settings. No local automated test suite run for docs/bootstrap. Readiness still blocked
  on fresh TEST target proof, exact runtime/client/session, logging controls and
  uncertainty plan. See docs/product/scoped-test-exercise-preparation.md.

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

October22 Cloud observations: Test API access, OAuth External/Testing, one test
user; Branding/publish and home/privacy/terms/domain incomplete. Owner reported
no domain on October19; ownership status not rechecked today. No upgrade, publish, purchase, new
scope or real account action. Exact current grant expiry was not inspected.
Domain/business/contact, real data recipients/retention/legal review, production
vault/tenant identity, fresh provider evidence, durable restore barriers, configured
DB recovery, current campaign staging E2E and schema rollback remain open. Real
metrics, commercial credit/payment/refund terms and enforceable campaign/aggregate
financial consent/caps must be resolved before real publishing.

## Next action

Complete the exact scope of fresh TEST-target verification (the existing verifier
reads/refreshes the preserved grant) and the isolated runtime/client binding.
No such credential/provider operation occurred in preparation. Do not enable flags
or start OAuth until evidence, session/logging/uncertainty gates and specific
exercise consent are satisfied. Preserve legacy grant/ledgers and stop/reconcile.
