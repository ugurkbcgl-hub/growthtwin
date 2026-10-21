# GrowthTwin — current handoff

Verified: 2026-10-21 21:06 Europe/Istanbul (+03:00).

## Objective and authorization

Türkiye self-service advertising across industries; clinic is only an example.
Normal advertiser journey should need no GrowthTwin staff operator. Develop local
synthetic slices while production gates remain open. Reviewed green PRs may squash
merge under standing owner authorization; never force merge, disable checks,
push main directly or enable auto-merge. No new paid services, real advertiser
connection/data, production publication, media spend or production AI in this slice.

## Repository and CI

Verified base main 93e53a2: PR #300 merged. Latest-head required CI 39647636463
passed 377 PostgreSQL tests including concurrency and 10 browser E2E tests;
post-merge main CI 39648069200 passed. No open PR at session start.
Current branch feat/synthetic-connection-work-guard, PR #301; implementation
head a1d8180. Required CI 39649688737 queued at this snapshot, which precedes
its own follow-up commit. Verify current
branch, worktree, latest head, open PR/checks before acting.

## Current slice — synthetic connection/work guard

- New SyntheticConnectionScope table: owner workspace, fixture UUID/generation,
  quarantine/open/blocked state, revision and fake work counter. No credentials.
  Registration is explicit/internal for fixed examples; retry cannot reopen.
- Only current registered OPEN scope/generation/revision runs fixed local fake
  CREATE/REFRESH/CALLBACK_SAVE. Missing/unknown/quarantined/invalid scope denies.
  Any closure blocks work independently of its outcome/generation or scope state.
- Closure intake and fake work first lock the owned workspace row. Closure and
  scope block commit together; issuance failure rolls back both. Earlier fake
  work can finish first; later callbacks cannot reopen or write a fake result.
- 14 new local guard tests + prior focused tests: 108 passed, five PostgreSQL
  races skipped on SQLite and await required CI. Two new tests cover both close/
  fake orderings. Ruff/migration drift and independent read-only review passed.
- New migration 0002 applied only to ephemeral local test DBs. Google/preview DBs,
  encrypted grant, immutable ledgers, Heroku and UI unchanged. No browser run for
  this service-only slice. No arbitrary executor, real provider/credential write,
  production restore proof or protection for already-sent network actions.

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

After reviewed guard PR passes required CI and merges, start accepted plan step 3:
unify the existing local synthetic advertiser journey with a clear stage overview
for campaign creation, current creative selection, plan/budget review, consent,
TEST dispatch status and reporting. Reflect unavailable/incomplete stages honestly;
no provider/credential read on ordinary GET, no new real data or execution. Keep
owner/tenant scope and existing fixed TEST ledgers. Actual runtime guard mapping
above remains a production gate, not something the fixture guard proves.

## Preserved local environments

- Preserve LocalAppData/Temp/gwt-oauth-isolated-wq0dp50j/synthetic.sqlite3,
  owner/workspace identity, encrypted grant and both immutable dispatch ledgers.
  Use helper LocalAppData/Temp/growthtwin_oauth_preserved.py, never the older
  fresh-DB bootstrap. Do not reset ledgers or reauthorize needlessly. DPAPI secrets
  are outside Git under LocalAppData/GrowthTwinsecrets; do not read/print values.
- Browser fixture 127.0.0.1:8011 (session 93512 at last check) has a separate
  validated Temp/gwt-closure-ui-preview-28gfu4nv/fixture.sqlite3, isolated session/
  CSRF cookies, unusable-password owner and Google features disabled. Helper:
  LocalAppData/Temp/growthtwin_closure_journey_preview.py. Its /__preview__/ entry
  creates only that fixture session; this is not a product login route or real
  sign-in test. Current slice did not restart/migrate the fixture server; running
  Python code may still be prior version. Server lifetime is ephemeral. No agent
  remains working; no secrets belong in handoff, logs, source or chat.
