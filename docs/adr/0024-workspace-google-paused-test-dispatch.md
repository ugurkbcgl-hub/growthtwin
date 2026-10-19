# ADR-0024: Durable workspace Google PAUSED TEST dispatch

- Status: Accepted for isolated local synthetic testing only
- Date: 2026-10-19
- Decision owner: Project owner, delegated implementation

## Decision

Add a separate one-to-one draft ledger referencing its exact immutable approval.
Never reset/reuse the fixed-test ledger from ADR-0022. Current source, selection,
owner/workspace, target/grant and signed ten-minute dispatch review must match.
Commit intent before creation; a repeated or uncertain request only reconciles.
Validate-only runs before reservation; rejected validation creates nothing.

The second explicit TEST consent shows these differences from the original plan:

- Preserve the exact original URL in the approved source. Use example.com only
  as an explicitly displayed test override, not a verified advertiser destination.
- Divide TRY minor-unit total by inclusive flight days, floor to whole kuruş,
  then multiply by 10000 to micros. Reject less than one kuruş per day. This is
  an average daily virtual budget, not a platform-enforced total spending cap.
- Map dates to account-local startDateTime 00:00:00 / endDateTime 23:59:59;
  require TRY and Europe/Istanbul (or its Asia/Istanbul alias) from the test account.
- Resolve exactly one ENABLED Ankara/TR/City geo constant; use PRESENCE only.
- Use one fixed synthetic EXACT keyword; selected approved headline/description
  assets are sent unchanged from the reviewed mapper output.
- Atomically create campaign/group/keyword/ad PAUSED. No enable operation exists.

Before every action verify the exact configured non-manager TEST account. All
existing local loopback, DEBUG-off, owner/workspace, encrypted grant and CSRF
guards remain. GET pages make no Google request. Single isolated process only;
this does not establish distributed concurrency, production auditing or caps.

Readback checks campaign/budget linkage, amount, date-times, PRESENCE, location,
keyword, group/ad PAUSED state, exact text assets and test URL. Stop uses recorded
target/name/resource identity and can send PAUSED despite changed current source
or remote budget/dates; full reconciliation can still remain uncertain after drift.
Unknown identity or changed grant/target requires recovery review, not a new create.
An independent status page preserves read/stop access after source edits/expiry.

## Evidence

71 focused local connection/mapper tests passed, including committed timeout,
no resend, stale input/target, final-verification source edit, CSRF, currency,
ambiguous geo and remote-drift stop. Browser created the selected synthetic draft,
read the mapped resources and confirmed stop as PAUSED through Google v25.
Migration 0008 applied only to the preserved isolated synthetic review database.
No live ads, media spending, advertiser data, production deployment or new service.

Official schema references checked 2026-10-19:

- https://developers.google.com/google-ads/api/docs/campaigns/budgets/overview
- https://developers.google.com/google-ads/api/docs/campaigns/budgets/create-budgets
- https://developers.google.com/google-ads/api/reference/rpc/v25/Campaign
- https://developers.google.com/google-ads/api/data/geotargets

Live validation rejected obsolete startDate/endDate JSON fields before any
reservation. Switching to v25 startDateTime/endDateTime passed validation.
