# GrowthTwin — current handoff

Verified: 2026-10-22 12:34 Europe/Istanbul (+03:00).

## Objective and authorization

Türkiye self-service advertising across industries; clinic is only an example.
Normal advertiser journey should need no GrowthTwin staff operator. Develop local
synthetic slices while production gates remain open. Reviewed green PRs may squash
merge under standing owner authorization; never force merge, disable checks,
push main directly or enable auto-merge. No new paid services, real advertiser
connection/data, production publication, media spend or production AI in this slice.

## Repository and CI

Verified base main3eb143e: PR308 merged. Latest-head CI39752232154 passed527
PostgreSQL tests and11 browser E2E tests; main CI39752610827 passed. No open PR
at slice start. Current branch feat/connection-recovery-dispositions, PR309; implementation head
afa2f49. Initial CI39756385104 running at this snapshot, which precedes its own
follow-up commit. Verify latest head/checks before merge. PR309 attachment failed
once at the known100-item limit; GitHub PR intact. Remove no unrelated attachments.

## Current slice — recovery assessment and synthetic reopening

- Owned candidate metadata assessment preserves uncertainty despite elapsed time,
  session loss/block/rotation. No retry/activation, secret I/O or candidate mutation.
- Double-default-off synthetic recovery GET lists20 recent owned fake receipts.
  Signed session/owner/scope/scenario/expiry-bound confirmed CSRF POST changes ONLY
  last-example marker. No begin/perform, new receipt or deadline extension. Actual
  candidate/grant is never rebound; existing runtime/legacy access unchanged.
- Stale/expired/running/terminal reopened examples cannot gain run controls.
  Current pending fake still requires separate confirmed perform and DB checks.
-18 new tests plus17 prior journey tests:35 local passes. Extended isolated browser
  passed new-session404, explicit same-receipt reopen, separate result execution,
  desktop/mobile/keyboard and preserved quarantine. Recovery mobile screenshot
  reviewed in Temp/growthtwin-authorization-recovery-20261022.
- Independent review found no blocker and requested stronger stale/expired/terminal
  tests; added/passed. Independent final re-review found no blocker; required CI follows. No migration or
  actual credential/provider/preserved Google/fixture DB/Heroku operation.
  See ADR0034. No automatic retry/revoke/adoption.

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

Complete this recovery PR/required CI/merge and main CI. Then implement explicit
RESERVED-only retirement with generation fencing and mocked tests; never retire
or retry EXCHANGING/UNCERTAIN, touch legacy grants or infer provider revocation.
Actual adapter remains off; callback/recovery wiring, configured TEST target proof,
orphan reconciliation and adoption/rollback remain prerequisites to rollout.
