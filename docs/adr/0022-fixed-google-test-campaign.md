# ADR-0022: Fixed Google test campaign lifecycle

- Status: Accepted for isolated local test use only
- Date: 2026-10-19
- Decision owner: Project owner (explicit test campaign instruction)

## Decision

Add a separate, disabled-by-default test campaign operation to the local Google
connection screen. This is not dispatch of arbitrary workspace drafts. Use a
fixed synthetic Search campaign, example.com destination, synthetic exact keyword
and responsive search text. Budget is one unit of the test account currency per
day. Campaign, ad group and ad start PAUSED. There is no enabling operation.

Before every external action, confirm the exact configured customer through its
configured manager is a non-manager test account. Missing identity or failed
verification prevents the action. Reuse existing local owner/workspace/session,
CSRF, loopback, DEBUG-off and encrypted credential boundaries.

Persist one workspace operation UUID/configuration fingerprint before the create
request. The workspace relationship protects its ledger from accidental cascade
deletion. The ledger is not a production audit system. Atomically create related
Google resources with partial failure disabled. Never resend an existing create
intent, even after timeout or restart. Reconcile by deterministic operation name;
zero, multiple or mismatched results cannot authorize a fresh create.

Read affects only the tracked operation. Stop sends PAUSED and confirms it by
readback; it does not delete resources. A stopped local operation is terminal for
creation. Test objects remain in the test account for inspection. Target or grant
changes block the old operation and require deliberate recovery review.

## Limits

The current app remains a single isolated Windows process. Tests/SQLite do not
prove production concurrency or financial controls. Test accounts do not serve
ads; results do not validate creative quality, delivery, performance, policy
approval, live publishing, advertiser data handling or a media-spend ceiling.

Official create examples checked 2026-10-19:
https://developers.google.com/google-ads/api/docs/campaigns/create-campaigns
https://developers.google.com/google-ads/api/samples/add-campaigns
