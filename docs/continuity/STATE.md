# GrowthTwin — current handoff

Verified: 2026-10-22 11:27 Europe/Istanbul (+03:00).

## Objective and authorization

Türkiye self-service advertising across industries; clinic is only an example.
Normal advertiser journey should need no GrowthTwin staff operator. Develop local
synthetic slices while production gates remain open. Reviewed green PRs may squash
merge under standing owner authorization; never force merge, disable checks,
push main directly or enable auto-merge. No new paid services, real advertiser
connection/data, production publication, media spend or production AI in this slice.

## Repository and CI

Verified base main9132e1e: PR306 merged. Latest-head CI39722697389 passed487
PostgreSQL tests and10 browser E2E tests; main CI39722996360 passed. No open PR
at slice start. Current branch feat/scoped-candidate-readback, PR307; implementation head
3e3758d. Initial required CI39747720288 running at this snapshot, which precedes
its own follow-up commit. Verify latest head/checks before merging. PR307
attachment failed once with the known100-item limit; GitHub PR is intact. Do not
remove unrelated attachments.

## Current slice — scoped candidate advisory readback

- Shared strict version-one codec validates exact keys, owned receipt binding,
  scope/client and bounded refresh material. Legacy/unknown/mismatched envelopes
  are rejected. Writer uses the same codec; no current runtime reader changes.
- Default-off unwired inspection permits candidate-only readback for committed
  current quarantined receipts. Pending/rejected/uncertain dispositions never
  promote an orphan. Ownership/session and current scope are checked before I/O;
  fresh scope/immutable receipt/client/legacy checks follow it. Match is advisory,
  not permission, actual token validity or independent recovery evidence.
- Five-minute handshake/write deadline does not expire stored inactive candidates.
  No activation, metadata/file mutation, auto retry/revoke/unlink or provider call.
-21 new local tests and1 PostgreSQL race; focused readback/adapter/backend run:
  55 local passes,3 PostgreSQL skips. Ruff/format and migration drift checks run;
  independent source review and final re-review found no blocker. Broad exception
  assertion tightened to PermissionDenied; required CI follows. No browser check.
- All client/path/transport/encrypted read/write mocked. No migration or actual
  credential/file/provider/preserved Google/fixture DB/Heroku operation. See ADR0032.

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

Complete this reviewed readback PR, required CI, squash merge and main CI.
Then design/rehearse owner/session/CSRF endpoint wiring with explicit fixtures,
keeping the real adapter off. Before actual hook rollout, configured TEST target
proof, pending/orphan recovery handling, explicit legacy adoption/rollback,
scoped refresh and separately permitted stop/reconcile remain open. No activation
or actual credential/file/provider access is authorized by this preparation.
