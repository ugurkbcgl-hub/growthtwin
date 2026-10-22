# GrowthTwin — current handoff

Verified: 2026-10-22 13:10 Europe/Istanbul (+03:00).

## Objective and authorization

Türkiye self-service advertising across industries; clinic is only an example.
Normal advertiser journey should need no GrowthTwin staff operator. Develop local
synthetic slices while production gates remain open. Reviewed green PRs may squash
merge under standing owner authorization; never force merge, disable checks,
push main directly or enable auto-merge. No new paid services, real advertiser
connection/data, production publication, media spend or production AI in this slice.

## Repository and CI

Verified base main89be175: PR309 merged. Latest-head CI39756480228 passed545
PostgreSQL tests and11 browser E2E tests; main CI39756903416 passed. No open PR
at slice start. Current branch feat/retire-reserved-candidate, PR310; implementation headbf82bfe.
Initial required CI39761074417 running at this snapshot, which precedes its own
follow-up commit. Verify latest head/checks before merge. PR310 attachment failed
once at the known100-item limit; GitHub PR intact. Remove no unrelated attachments.

## Current slice — explicit RESERVED-only retirement

- Default-off unwired metadata service requires typed scope/request and explicit
  confirmation. Locks owned workspace/connector/attempt. Only current quarantined
  RESERVED and no other unresolved history can retire. Every other state denies.
- Generation rotation and original REJECTED/retired_before_exchange write share one
  transaction. Permanent unique request/replacement-generation binding validated;
  failed final write/validation rolls both back. History/deadlines preserved.
- Exact replay returns current identity after later rotate/block; never reopens.
  Old callback sealed by terminal receipt/generation, no process-store cleanup.
  No retry/revoke/unlink/activation/adoption or actual legacy/runtime change.
-14 new local tests plus2 PostgreSQL races; with adapter/recovery:42 local passes,
  4 PostgreSQL skips pending CI. Independent final review found no blocker.
  Races cover exchange-first deny and retirement-first zero callback transport.
- Migration0006 only in ephemeral test DBs; no actual credentials/provider/files/
  preserved Google/fixture DB/Heroku/UI operation. No manual browser check.
  See ADR0035. Required CI must verify PostgreSQL races before merge.

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

Complete this retirement PR/required CI/merge and main CI. Then separately wire
scoped start/callback/retirement endpoints with session/CSRF and mocked transport
tests, keeping normal runtime off. Configured TEST target proof, uncertain/orphan
reconciliation, legacy adoption/rollback, scoped refresh and production gates
remain open; do not infer actual grant revocation or provider permission.
