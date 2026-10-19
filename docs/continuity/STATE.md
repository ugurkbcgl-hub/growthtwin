# GrowthTwin — current handoff

Verified: 2026-10-19, Europe/Istanbul.

## Objective

Self-service advertising for Türkiye across industries. Current milestone is
local Google OAuth authorization; live publication remains gated.

## Repository

Base main: `58293a3` (merged PR #282). Current branch
`fix/local-oauth-form-origin`, PR #283. Verify its current commit and CI because
this snapshot precedes its own commit. No legacy database was modified.

## Verified progress

- Local-only start/callback/disconnect uses state/PKCE, owner/workspace/session
  binding, CSRF and Windows user-scoped DPAPI outside Git.
- Real browser found Origin null caused by no-referrer on the form. Form now
  uses same-origin; callback remains no-referrer. CSRF stays enforced.
- Real Google exchange then reached storage but failed because the browser-
  launched environment lacked executable resolution for the Windows ACL tool.
  Restoring standard PATHEXT in the helper fixed this; a fabricated write/read
  roundtrip passed in that same process environment.
- October 19: owner completed Google identity verification and explicitly
  approved the broad Ads OAuth scope. Google returned successfully. The local
  page displayed both authorization record present and encrypted save success.
- The active isolated local server holds the disposable owner/workspace and
  session. Preserve this database/identity for follow-up; do not recreate IDs
  and inadvertently associate the saved grant with a different local owner.
- 35 focused local tests passed, plus live browser authorization/save verified.
  Google Ads API account verification or campaign operations have not run.

## Google configuration

Dedicated test manager/child and Cloud project with Test API access exist.
OAuth client External/Testing, one test user; exact loopback redirect registered.
Client and refresh credentials are protected outside Git under the current
Windows user's LocalAppData/GrowthTwinsecrets. Do not print their values.

## Limits and next action

Single local Windows process only; DEBUG off, explicit owner/workspace,
loopback host/peer and no proxy. No production or staging activation.
Legacy recovery, usability and real advertiser release gates remain unresolved.

Next: implement a narrowly scoped read for the explicit test customer/manager,
refreshing the saved grant securely and verifying the returned test_account flag
before any further account query or mutation. Never enumerate unrelated accounts,
publish or spend as part of this check.
