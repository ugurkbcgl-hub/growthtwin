# GrowthTwin — current handoff

Verified: 2026-10-22 07:06 Europe/Istanbul (+03:00).

## Objective and authorization

Türkiye self-service advertising across industries; clinic is only an example.
Normal advertiser journey should need no GrowthTwin staff operator. Develop local
synthetic slices while production gates remain open. Reviewed green PRs may squash
merge under standing owner authorization; never force merge, disable checks,
push main directly or enable auto-merge. No new paid services, real advertiser
connection/data, production publication, media spend or production AI in this slice.

## Repository and CI

Verified base main6648139: PR304 merged. Latest-head CI39719120618 passed440
PostgreSQL tests including new identity races and10 browser E2E tests; main
CI39719367350 passed. No open PR at slice start.
Current branch feat/synthetic-authorization-attempts, uncommitted implementation
at this snapshot; new PR/CI not created yet. Recheck live state/head/checks.
PR attachment has hit this chat's100-item limit; attempt once per new PR,
do not remove unrelated attachments. GitHub PRs remain intact.

## Current slice — generation-bound synthetic authorization attempts

- Internal default-off rehearsal with fixed typed confirmation/scenario,10-minute
  expiry and owned connection/generation/revision binding. One active attempt per
  connection. No OAuth code/state/PKCE/session, credential or external evidence.
- Running reservation commits before fixed local fake; final result rechecks
  ownership, registry state/generation/revision, switch, expiry and immutable
  binding. Replay/duplicate running/terminal calls do not execute the fake again.
- Block/rotation/expiry/disable while fake runs rejects late success. Accepted is
  only an ALLOW example with aware completion inside lifetime; identity stays
  quarantined. Failed persistence/running receipt is never automatically resumed.
-23 new local tests +15 identity tests passed (38 total);4 PostgreSQL races skip
  locally (2 new). Ruff/format/migration drift and independent re-review passed.
  Review finding about corrupt accepted metadata fixed with two regressions.
- Migration0004 applied only to ephemeral test DBs. Preserved Google/fixture DBs,
  grants, ledgers, provider, Heroku and UI unchanged. No browser test needed.
- ADR0030 records scope; this is not OAuth callback authenticity, grant storage,
  provider permission or production restore/no-resend proof. Existing runtime
  remains unconnected and cannot consume the synthetic accepted metadata.

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

Finish this reviewed attempt PR/required CI/merge and verify main CI. Then
review the Google TEST credential-envelope/callback adoption and rollback plan
from source and implement a default-off adapter boundary with mocked pre/post
exchange/result checks, explicitly bound to durable identity/generation. Do not
read/migrate/reactivate/reset the preserved grant in that preparation. Actual
OAuth integration, separately allowed stop/reconcile, production privacy/access/
recovery/financial gates remain open. Synthetic accepted metadata is never a grant.

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
