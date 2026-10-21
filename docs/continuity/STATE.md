# GrowthTwin — current handoff

Verified: 2026-10-21 21:28 Europe/Istanbul (+03:00).

## Objective and authorization

Türkiye self-service advertising across industries; clinic is only an example.
Normal advertiser journey should need no GrowthTwin staff operator. Develop local
synthetic slices while production gates remain open. Reviewed green PRs may squash
merge under standing owner authorization; never force merge, disable checks,
push main directly or enable auto-merge. No new paid services, real advertiser
connection/data, production publication, media spend or production AI in this slice.

## Repository and CI

Verified base main 7dfdf6a: PR #301 merged. Latest-head required CI 39649793207
passed 393 PostgreSQL tests including concurrency and 10 browser E2E tests;
post-merge main CI 39650308546 passed. No open PR at slice start.
Current branch feat/campaign-journey-overview, PR #302, implementation head
2ae5f9f. Required CI 39652954215 in progress at this snapshot, which precedes
its own follow-up commit. Verify live branch/worktree/latest head/checks.
PR attachment to this chat failed once: attachment identity count exceeds 100;
GitHub PR is intact. No unrelated attachments were changed.

## Current slice — campaign stage overview

- Owner-scoped read-only /workspace/campaigns/<id>/journey/ joins six existing
  stages with advisory next action and list/detail/report navigation.
- Current creative preference is not consent; approval existence is not verified
  current consent. Stored TEST status is unrefreshed and may refer to old source.
  Existing dispatch takes priority over new submission after source changes.
- GET/HEAD reads scoped metadata only, no payload/grant/provider/write; unsafe
  methods rejected, errors private/no-store/noindex. Exact existing loopback
  settings and prerequisites govern links, not endpoint authorization.
- 16 new + 47 existing focused tests: 63 passed, no skips. Ruff/formatting,
  migration drift and independent read-only review passed. No new migration.
- Browser created fixture draft 1 and selected current creative; next action
  changed to plan review. Plan/report Enter navigation and list roundtrip passed.
  Desktop and 390x844 viewport inspected, mobile widths 375/375; viewport reset.
  Screenshots campaign-journey-desktop.png and campaign-journey-mobile.png outside
  Git in conversation workspace. No actual Google operation or product login.
- ADR-0028 records the read-only/advisory contract; latest-head required CI still required.

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

Finish reviewed journey PR/required CI/merge and verify main CI. Then carry
campaign overview navigation into existing protected TEST review/status screens,
with explicit fixed TEST consent and stored-versus-refreshed status labels.
Preserve exact loopback/owner/CSRF/immutable-ledger boundaries and no-resend/stop
behavior. Ordinary overview GET must not read grants or call providers. Production
identity/privacy/access/recovery/financial gates and actual guard mapping stay open.

## Preserved local environments

- Preserve LocalAppData/Temp/gwt-oauth-isolated-wq0dp50j/synthetic.sqlite3,
  owner/workspace identity, encrypted grant and both immutable dispatch ledgers.
  Use helper LocalAppData/Temp/growthtwin_oauth_preserved.py, never the older
  fresh-DB bootstrap. Do not reset ledgers or reauthorize needlessly. DPAPI secrets
  are outside Git under LocalAppData/GrowthTwinsecrets; do not read/print values.
- Browser fixture 127.0.0.1:8011 (session 59045 at last check) has a separate
  validated Temp/gwt-closure-ui-preview-28gfu4nv/fixture.sqlite3, isolated session/
  CSRF cookies, unusable-password owner and Google features disabled. Helper:
  LocalAppData/Temp/growthtwin_closure_journey_preview.py. Its /__preview__/ entry
  creates only that fixture session; this is not a product login route or real
  sign-in test. Current slice restarted this isolated fixture and applied prior migration 0002
  there. Draft 1 is the new journey example; prior closure examples retained. Server lifetime is ephemeral. No agent
  remains working; no secrets belong in handoff, logs, source or chat.
