# GrowthTwin — current handoff

Verified: 2026-10-19 13:45 Europe/Istanbul (+03:00).

## Objective

Türkiye self-service advertising across industries. Local synthetic Google
workspace draft approval and PAUSED TEST create/read/stop work. Live advertiser
data, production serving and media spend remain gated.

## Repository

Base main bfc7397 (PR #287 merged); its required CI 39237793375 and main CI
39238090433 passed. Current branch feat/google-total-budget-validation.
This snapshot precedes its PR/commit; recheck live Git/open PR/CI before work.
Reviewed green PRs may be merged under standing owner authorization.

## Current verified result

- Readiness audit is docs/product/google-search-live-readiness.md: distinct real
  account/API, advertiser financial consent, destination, total/account cap,
  policy/privacy, recovery/deployment and report/commercial gates remain open.
- Corrected historical DEPLOYMENT E2E/rollback claims from existing dated evidence;
  did not recheck Heroku or inspect/export legacy data. Old gap/API research is
  explicitly historical; local TEST integration is real, live integration is not.
- New signed local owner CSRF POST validates a separate campaign-total-budget
  candidate with CUSTOM_PERIOD and exact totalAmountMicros. Only validateOnly=true
  is sent after TEST account/TRY/timezone/geo/current approval checks. No create,
  ledger reset or daily fallback. Source/target rechecked before/after request.
- Browser: Google v25 TEST accepted the 5,000 TRY candidate. This spends nothing,
  creates nothing and does not apply a cap to the existing daily-budget campaign.
- 79 focused local connection/mapper tests, Ruff and system check passed. Reviewer
  identified network/shape failure handling; sanitized HTTP409 regression added.
  PR and post-merge CI for this change must be checked live after publishing.
- No new migration, paid infrastructure, production account or deployment.

## Next action

Implement and verify a NEW durable PAUSED TEST total-budget dispatch profile:
explicitly reviewed CUSTOM_PERIOD/totalAmountMicros/dates, committed intent and
exact readback/stop. Preserve existing daily-budget resources/ledgers and their
read/stop access; no type conversion, reset or silent daily fallback. Real
publication and spend still require the separate live-readiness gates.

## Local environment

Preserve LocalAppData/Temp/gwt-oauth-isolated-wq0dp50j/synthetic.sqlite3,
owner/workspace identity, encrypted grant and both durable ledgers. Helper:
LocalAppData/Temp/growthtwin_oauth_preserved.py. Never run the older fresh-DB
bootstrap or reset existing intent. Generated local login is not recorded.
The latest browser /connections/google/total-budget-validate/ displayed successful validation-only. The earlier draft-dispatch result was stopped / PAUSED; the daily ledger remains unchanged.
Status controls: /connections/google/draft-status/?draft=1. Server/helper
availability is ephemeral; verify before use. Grant stored with user-scoped
Windows DPAPI outside Git; reuse it rather than unnecessary reauthorization.
Read-only reviewer completed; no agent work remains running.
