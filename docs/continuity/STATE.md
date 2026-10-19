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

## Verified API milestone

October 19: a controlled local verifier refreshed the saved grant, then made one
fixed GAQL Search request against only the owner-designated test child through
its designated test manager. The response contained exactly one matching child,
`testAccount=true` and no manager flag. No account enumeration, campaign data,
mutations or spend. Only booleans/counts were emitted; identifiers and credentials
were excluded from repository notes. The verifier is a temporary local script,
not yet a product route or reusable application adapter.

## Application verification UI

The read is now an application adapter with explicit test customer/manager
settings. The local owner uses a CSRF-protected POST to verify; GET never calls
Google. Matching test-account evidence is session-local, expires after ten
minutes, and is invalidated by changed target/owner/workspace/encrypted grant,
failed verification or disconnect. Missing targets and non-test/mismatched
responses fail closed. No IDs or tokens appear in the UI.

Live browser verification through the new button succeeded on October 19.
47 focused local tests passed; Ruff passed. The existing isolated synthetic
database and owner/workspace were preserved for the saved credential.
Current branch: feat/google-test-connection-status; snapshot precedes its PR.

Next: design the narrowly scoped paused synthetic campaign creation/stop
adapter using the verified test target, explicit action authorization and
idempotency. Do not enable live serving or media spend.