# Google Ads local test integration

Verified: 2026-10-19, Europe/Istanbul.

## Current evidence

Dedicated Google test manager/child and Cloud project with Test access exist.
OAuth is External/Testing with one test user and the exact loopback callback
registered. The owner approved the broad Ads scope; encrypted authorization
save and refresh succeeded. Credentials remain outside Git under the current
Windows account's LocalAppData/GrowthTwinsecrets using user-scoped DPAPI.

The application verifies only the configured child through its manager, accepts
exactly one matching non-manager test account, and displays recent session-local
evidence for up to ten minutes. Changes to targets, owner/workspace or encrypted
grant invalidate that evidence. GET does not call Google.

## Fixed paused test campaign

The owner explicitly authorized a synthetic campaign create/read/stop rehearsal.
The local connection screen now exposes it behind the additional
`GOOGLE_ADS_LOCAL_TEST_CAMPAIGN_ENABLED=true` flag. All local OAuth guards remain.
The operation uses a fixed synthetic Search campaign, ad group, exact keyword,
responsive search ad and example.com destination. Campaign, group, keyword and
ad start PAUSED. Virtual daily budget: one unit of the account currency.

Live browser evidence on October 19:

- Google validation-only request succeeded before durable intent reservation.
- One atomic create request produced the fixed test resources.
- Initial reconciliation failed because Google named the non-shared budget
  after the campaign; the reader was corrected to accept that observed name
  while also requiring exact budget resource linkage, target, type and amount.
- Read recovered the SAME campaign without resending create and confirmed PAUSED.
- Stop sent PAUSED and read it back; the UI displayed stop confirmed / PAUSED.
- Repeating create after stop read the same durable operation; no new create.

One workspace ledger is committed before the real request. Uncertain requests
are never automatically resent; zero/multiple/mismatched reads remain uncertain.
Workspace deletion is protected while the ledger exists. Existing credential or
target changes block the old operation. Stop pauses; it does not delete objects.
The fixed test journey is separate from the fake workspace rehearsal and does
not yet dispatch arbitrary customer campaign drafts. See ADR-0022.

## Local operation requirements

Windows only, DEBUG off, single process without autoreload, exact loopback
host/peer, no proxy/forwarded headers, explicit local owner/workspace and:

- GOOGLE_ADS_LOCAL_OAUTH_ENABLED=true
- GOOGLE_ADS_LOCAL_OWNER_ID and GOOGLE_ADS_LOCAL_WORKSPACE_ID
- GOOGLE_ADS_LOCAL_TEST_CUSTOMER_ID and GOOGLE_ADS_LOCAL_TEST_MANAGER_ID
- GOOGLE_ADS_LOCAL_TEST_CAMPAIGN_ENABLED=true (only for test mutations)

Preserve the active isolated synthetic database and its owner/workspace identity
for the encrypted grant and durable ledger. Never recreate those IDs under a
new identity or delete/reset uncertain intent to bypass duplicate protection.
Migration 0006 was applied only to this isolated test database during browser
verification; existing legacy/local configured DB and Heroku were not migrated.

The form uses same-origin referrers for CSRF; callbacks use no-referrer. Helpers
sanitize errors and suppress callback-bearing Django console logs. These are
not proxy/router logging controls or a production secret store.

## Verification and limits

52 focused local tests passed; formatting/lint and migration consistency passed.
Live Google create/read/stop was verified through the application. Current PR CI
must be checked before merge. SQLite cannot prove production concurrency.

Google test accounts do not serve advertisements or incur media spend. No live
serving, advertiser data, performance results, paid service or production rollout
was enabled. Next bind a reviewed synthetic workspace draft to an immutable
platform payload and explicit dispatch consent before broadening this fixed test.

## Official references

- https://developers.google.com/google-ads/api/docs/campaigns/create-campaigns (checked October 19)
- https://developers.google.com/google-ads/api/samples/add-campaigns (checked October 19)
- https://developers.google.com/google-ads/api/docs/api-policy/developer-token (checked October 17; Cloud-based access supersedes tokens)
- https://developers.google.com/identity/protocols/oauth2/web-server (checked October 17)


## Workspace review preparation — 2026-10-19

ADR-0023 adds an owner-only local review package from the selected workspace creative and plan. Canonical JSON and a source/target-bound signed review prevent silent changes; POST approval stores an immutable snapshot. 62 focused tests passed and the synthetic browser approval succeeded without any Google call. Existing fixed-test dispatch is unchanged. Migration 0007 applied only to the preserved synthetic review DB. Destination example.invalid remains exact and unverified; future dispatch must explicitly resolve destination, budget/date/targeting semantics and revalidate current approval before a new durable Google operation.


## Workspace PAUSED TEST dispatch — 2026-10-19

ADR-0024 implements the separate durable workspace draft dispatch after ADR-0023 approval. The UI additionally displays and requires consent for the example.com test URL override, inclusive daily TRY budget (rounded down to kuruş), account-local date-times, Ankara/PRESENCE and synthetic EXACT keyword. It preserves the original example.invalid URL in the approval. Before writes, Google verifies the configured TEST child, TRY currency, Türkiye time zone and one enabled city constant. Validation-only passed with v25 date-time fields; the subsequent browser create/read/stop succeeded. Readback checks creative assets, destination, budget, dates and targeting. 71 focused tests passed.

Migration 0008 was applied only to the preserved isolated synthetic DB. Each draft has a separate one-to-one intent referencing the immutable approval; uncertain requests never resend creation. /connections/google/draft-status/?draft=1 preserves owner-only read/stop even after the current source becomes invalid. Remote drift can leave full reconciliation uncertain despite a sent pause; changed target/identity requires recovery review. No live account, serving, media spend or production readiness is established.


## Total budget candidate validation — 2026-10-19

ADR-0025 adds a separate signed local POST that constructs a CUSTOM_PERIOD / exact totalAmountMicros candidate and sends validateOnly=true only to the verified TEST child. Browser accepted the 5,000 TRY example; no Google resources or ledger rows were created/changed. The existing daily-budget test is unchanged and does not acquire a total cap. 79 focused tests passed. No daily fallback or live enable path exists. Next is a NEW durable PAUSED TEST total-budget profile, followed by the remaining [live-readiness gates](google-search-live-readiness.md).


## Total-budget PAUSED TEST resource — 2026-10-19

ADR-0026 extends new dispatch to v2 CUSTOM_PERIOD/exact totalAmountMicros. Google TEST created the new isolated synthetic draft 2 at 5,000 TRY (October 20–November 3), exact readback passed, repeat create reconciled the same record and stop confirmed PAUSED. Old draft 1 retained DAILY/333.33 TRY/November 1–15 and its read/stop also passed. No ledger conversion/reset or daily fallback exists; unknown versions/period/amount drift fail closed. 82 focused tests passed. This verifies configuration, not actual total-cap exhaustion or live spend controls. Existing validation-only endpoint stays non-creating.
