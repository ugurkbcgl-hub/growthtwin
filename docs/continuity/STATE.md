# GrowthTwin — current handoff

Verified: 2026-10-19 19:03 Europe/Istanbul (+03:00).

## Objective

Türkiye self-service advertising across industries. Local synthetic Google
DAILY/total-budget PAUSED TEST lifecycle works. Real data, production serving
and media spend remain gated.

## Repository

Main 38e3cce: PR #290 merged after required CI 39278829487 passed. Main CI
39281752320 is queued. PR #291 was rebased/retargeted to main, head 13f1dfa;
required CI 39281843423 is queued. PR #292, branch feat/public-information-pages,
builds on #291 (base docs/public-identity-requirements); latest head
5ea0b28, CI 39281961036 queued. Current branch docs/data-lifecycle-contract builds
on #292 and will target feat/public-information-pages until that PR merges.
This snapshot precedes its own commit/PR. Verify latest heads/bases/checks; merge in
dependency order, retargeting/rebasing the child when its parent is squash merged.
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
  home route exists; separate contact/privacy/terms routes are now implemented.
- Protected approval/dispatch snapshots include content. Do not promise immediate
  total deletion or delete durable no-resend intent to satisfy a naive cleanup.
- Implementation: static GET/HEAD-only /iletisim/, /gizlilik/ and
  /kullanim-kosullari/, shared links and public home footer. Visible draft labels,
  noindex, no forms/scripts or new data collection on these pages.
- Five focused SimpleTestCase tests passed without DB access, including anonymous
  access, links, method rejection, HEAD, no cookie writes and no query reflection.
  Ruff format/check and git diff --check passed. Desktop/mobile browser navigation,
  focus and layout reviewed; mobile document/client width 375/375, no horizontal
  overflow on info pages or home footer. Independent code review had no findings.
- Separate temporary preview at 127.0.0.1:8010 uses in-memory test DB and its own
  cookie name, not the preserved Google DB. Initial home error from an existing
  browser cookie was resolved by that cookie isolation; home then passed review.
  This preview supports information-page review, not campaign operation.
- ADR-0027 now defines category-specific retention/deletion/recovery boundaries,
  separate stop/revoke/secret/local/recipient/backup outcomes, no-resend barrier
  versus content snapshot, in-flight/callback races and restore quarantine.
  No production mechanism, model, migration, erasure or new duration was added.
  Official Google revoke and KVKK destruction regulation checked on October 19.
  Independent review found one misleading workspace-delete phrase; corrected to
  campaign-draft deletion. No other findings. git diff --check passed; no new
  local application tests run for this documentation-only step.

## Preserved product evidence

PR #289 browser verified new synthetic draft 2 with 5,000 TRY CUSTOM_PERIOD,
October 20–November 3, exact readback/repeat create/stop. Original draft 1 DAILY
333.33 TRY November 1–15 retained read/stop. 82 targeted tests passed in that
implementation. No production budget exhaustion/aggregate cap proof is implied.

## CI observation at this snapshot

PR #290 latest-head run 39278829487 is now confirmed success and #290 merged.
PR #291 and #292 currently show queued for their new heads. Auto-merge is not enabled; linear
history rules also reject merge commits, so use squash after checks pass.
No repository rule was changed. Do not force merge or disable checks.
Merge reviewed PRs in dependency order only when their own required checks pass.

## Next action

Settle the dependent PRs in order after required CI; then implement a pure
synthetic lifecycle decision contract from ADR-0027, returning allowed actions
and truthful independent outcomes. No DB/API/UI, token change or real erasure
in that slice. Check scope/authorization, uncertainty, late completion and
restore restrictions without pretending persistence/concurrency is solved.
Domain/business/contact, real recipients, retention periods and qualified review
remain open before final public text/production. Preserve TEST setup, immutable
existing ledgers and encrypted grant; no upgrade, publish, scope grant, purchase
or real advertiser/spend action now.

## Local environment

Preserve LocalAppData/Temp/gwt-oauth-isolated-wq0dp50j/synthetic.sqlite3,
owner/workspace identity, encrypted grant and both durable ledgers. Helper:
LocalAppData/Temp/growthtwin_oauth_preserved.py. Never run the older fresh-DB
bootstrap or reset existing intent. Generated local login is not recorded.
Latest browser draft-dispatch result for draft 2: stopped / PAUSED, 5,000 TRY CUSTOM_PERIOD. Original draft 1 remains stopped / PAUSED, 333.33 TRY DAILY. Preserve both ledgers and all draft IDs.
Status controls: /connections/google/draft-status/?draft=1. Server/helper
availability is ephemeral; verify before use. Grant stored with user-scoped
Windows DPAPI outside Git; reuse it rather than unnecessary reauthorization.
Read-only requirements and implementation reviews completed with no findings;
no agent work remains running. Google DB/grant/ledger unchanged. Preview proof
outside Git: conversation workspace information-contact-desktop.png and
information-mobile-footer.png. Server lifetime is ephemeral.
