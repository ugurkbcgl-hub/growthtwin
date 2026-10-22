# GrowthTwin — current handoff

Verified: 2026-10-22 12:02 Europe/Istanbul (+03:00).

## Objective and authorization

Türkiye self-service advertising across industries; clinic is only an example.
Normal advertiser journey should need no GrowthTwin staff operator. Develop local
synthetic slices while production gates remain open. Reviewed green PRs may squash
merge under standing owner authorization; never force merge, disable checks,
push main directly or enable auto-merge. No new paid services, real advertiser
connection/data, production publication, media spend or production AI in this slice.

## Repository and CI

Verified base main a060234: PR307 merged. Latest-head CI39747787250 passed509
PostgreSQL tests and10 browser E2E tests; main CI39748174729 passed. No open PR
at slice start. Current branch feat/synthetic-authorization-session-journey, PR308; implementation
head e0d6141. Initial CI39752146038 running at this snapshot, which precedes its
own follow-up commit. Verify latest head/checks before merging. PR308 attachment
failed once with the known100-item limit; GitHub PR is intact. Do not remove
unrelated attachments.

## Current slice — synthetic owner/session/CSRF journey

- New double-default-off fixture pages call only the fixed synthetic coordinator.
  Signed10-minute owner/workspace/session-HMAC/connection/generation/revision/
  attempt/scenario/action tickets and exact fields/confirmation protect two POSTs.
  Start reserves; separate perform runs the fake. GET never runs work; replay
  cannot duplicate it. Accepted example is never a grant or provider permission.
- Initiating session marker scopes status/result access; only LAST started example
  is accessible. Lost/rotated sessions or session-store failure after reservation
  have no UI recovery. Preserve pending history; do not auto-retry or activate.
-17 new endpoint tests plus coordinator:40 local passes,2 PostgreSQL skips.
  New browser test passed desktop/mobile/keyboard, fixed outcomes and refresh;
  source CSS screenshots reviewed in Temp/growthtwin-authorization-rehearsal-20261022.
- Independent review found missing framework-error header coverage. Prefix and
  three403/404 no-store/private/noindex regressions fixed. Independent final
  re-review found no blocking issue.
  Ruff/format, migration drift and whitespace checks run. No migration.
- Actual candidate adapter remains off/unwired. No actual provider, secret or credential file,
  preserved Google/fixture DB or Heroku action. Browser used ephemeral test DB.
  Existing dev Playwright pin installed locally; dependency manifests unchanged.
  See ADR0033 and its explicit session/recovery limits.

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

Complete this reviewed session-journey PR/CI/merge and verify main CI. Then
design/test explicit lost-session and pending/uncertain candidate recovery
dispositions, preserving legacy grants and separately permitted stop/reconcile.
Keep the actual adapter off. Configured TEST target proof, callback/recovery
wiring and explicit legacy adoption/rollback remain prerequisites to rollout.
