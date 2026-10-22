# GrowthTwin — current handoff

Verified: 2026-10-22 13:42 Europe/Istanbul (+03:00).

## Objective and authorization

Türkiye self-service advertising across industries; clinic is only an example.
Normal advertiser journey should need no GrowthTwin staff operator. Develop local
synthetic slices while production gates remain open. Reviewed green PRs may squash
merge under standing owner authorization; never force merge, disable checks,
push main directly or enable auto-merge. No new paid services, real advertiser
connection/data, production publication, media spend or production AI in this slice.

## Repository and CI

Verified base main29217c0: PR310 merged. Latest-head CI39761138226 passed561
PostgreSQL tests and11 browser E2E tests; main CI39761601822 passed. No open PR
at slice start. Current branch feat/scoped-candidate-endpoints, PR311; implementation head5a64e31.
Initial CI39765118546 running at this snapshot, which precedes its own follow-up
commit. Verify latest head/checks before merge. PR311 attachment failed once at
the known100-item limit; GitHub PR intact. Remove no unrelated attachments.

## Current slice — closed scoped TEST endpoint wiring

- New separate metadata overview/start/callback/retire routes; endpoint+candidate
  flags remain False. Existing exact configured owner/workspace/loopback8002,
  DEBUG False/no-forward guards apply. No legacy runtime/redirect/grant change.
- Signed5-minute session/scope/action forms and CSRF. State SHA256 marker (no raw
  state/code/verifier) rejects old/wrong callback before current nonce consumption.
  Allowed callback303 cleans URL; slashless alias avoids query-bearing redirect.
- Retirement digest now checked UNDER service locks following independent TOCTOU
  finding; regression mutates receipt between endpoint read and service lock and
  proves409/no retirement/rotation. Independent final re-review approved.
-25 new tests plus adapter/retirement/legacy:76 local passes,4 PostgreSQL skips.
  Ruff/format, migration drift and whitespace checks run. No new migration or
  actual provider/credential/files/preserved Google/fixture DB/Heroku operation.
  No manual browser check; request-level validation. CI pending.
- Separate scoped callback URI must be checked/configured with current isolated
  TEST target before enabling. No actual OAuth success, active grant, refresh,
  adoption or cleanup claim. See ADR0036 and its process/logging/rollout limits.

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

Complete scoped-endpoint PR/required CI/merge and main CI. Then verify isolated
TEST OAuth configuration/new redirect and current target readiness before any
separately authorized candidate exercise. Preserve legacy grant/ledgers; no
publishing, account upgrade, adoption, refresh or actual cleanup. Normal flags
remain off; reconciliation, rollback and production gates remain open.
