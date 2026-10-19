# GrowthTwin — current handoff

Verified: 2026-10-19 18:49 Europe/Istanbul (+03:00).

## Objective

Türkiye self-service advertising across industries. Local synthetic Google
DAILY/total-budget PAUSED TEST lifecycle works. Real data, production serving
and media spend remain gated.

## Repository

Base main 09f54cc (PR #289 merged); its required CI 39242010811 and main CI
39242328698 passed. PR #290 remains open at 59b688a; required run 39278829487
is queued, so it has not merged. Current branch docs/public-identity-requirements,
PR #291 (implementation head 514f75b), targets #290's branch until #290 merges.
Its initial CI 39280685026 is queued. This snapshot precedes its own follow-up
commit; verify latest Git/head/checks live. Retarget #291 to main after #290
merges, then check its latest-head required CI before merging it.
Reviewed green PRs may merge under standing owner authorization.

## Verified Cloud/OAuth observations — read-only

- Existing test Cloud project: Ads API Enabled, current access Test, 15,000 daily
  TEST operations. Explorer Apply for access visible, NOT clicked/submitted.
- OAuth External/Testing, one test user of 100. Publish app disabled until Branding
  complete. Home/privacy/terms URLs and authorized domain list empty. Verification
  Center says verification not required because Testing; not production approval.
- All three Data Access scope declaration tables empty. This does not invalidate
  the existing encrypted runtime adwords TEST grant or past TEST proof.
- Owner confirmed no domain yet. No purchase, new project/service, scope change,
  upgrade, publishing action or real advertiser connection occurred.
- docs/product/google-production-access-audit.md separates API access, OAuth
  publication and advertiser/financial readiness, with current official sources.
  Testing grant expiry is generally seven days for these scopes; exact current
  grant expiry was not inspected or calculated. Do not rotate needlessly.
- Requirements now in docs/product/public-identity-page-requirements.md:
  page acceptance criteria, code-derived data inventory, missing owner facts,
  retention/ledger deletion and test/production project separation. Existing
  home route exists; separate contact/privacy/terms routes are not implemented.
- Protected approval/dispatch snapshots include content. Do not promise immediate
  total deletion or delete durable no-resend intent to satisfy a naive cleanup.
- Documentation-only work: no new local application tests run. git diff --check
  passed before this snapshot; required/post-merge CI must be checked live.

## Preserved product evidence

PR #289 browser verified new synthetic draft 2 with 5,000 TRY CUSTOM_PERIOD,
October 20–November 3, exact readback/repeat create/stop. Original draft 1 DAILY
333.33 TRY November 1–15 retained read/stop. 82 targeted tests passed in that
implementation. No production budget exhaustion/aggregate cap proof is implied.

## CI observation at this snapshot

PR #290 prior-head runs 39277504638 and 39277581963 are now both success.
Latest-head run 39278829487 remains queued. Auto-merge is not enabled in this
repository; enabling it was not attempted. Do not force merge or disable checks.
Merge reviewed PRs in dependency order only when their own required checks pass.

## Next action

After settling the documentation PR dependency/checks, implement local static
/iletisim/, /gizlilik/, /kullanim-kosullari/ draft preparation pages and footer
links per public-identity-page-requirements.md. Explicit draft/not-ready labels,
no forms or data collection, no invented business identity, no Google changes.
Use focused route/template and visual checks appropriate to that implementation.
Domain/business/contact, real recipients/retention and qualified review remain
open before final public text/production. Preserve Test/Testing and plan separate
production project/credentials; no upgrade, publish, scope grant, purchase or real
advertiser/spend action now.

## Local environment

Preserve LocalAppData/Temp/gwt-oauth-isolated-wq0dp50j/synthetic.sqlite3,
owner/workspace identity, encrypted grant and both durable ledgers. Helper:
LocalAppData/Temp/growthtwin_oauth_preserved.py. Never run the older fresh-DB
bootstrap or reset existing intent. Generated local login is not recorded.
Latest browser draft-dispatch result for draft 2: stopped / PAUSED, 5,000 TRY CUSTOM_PERIOD. Original draft 1 remains stopped / PAUSED, 333.33 TRY DAILY. Preserve both ledgers and all draft IDs.
Status controls: /connections/google/draft-status/?draft=1. Server/helper
availability is ephemeral; verify before use. Grant stored with user-scoped
Windows DPAPI outside Git; reuse it rather than unnecessary reauthorization.
Independent read-only review of the requirements and source completed with no
actionable findings. No agent work remains running. No local DB/grant was read
or changed for the code-derived data inventory.
