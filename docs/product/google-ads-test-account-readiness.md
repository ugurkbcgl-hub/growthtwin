# Google Ads local test connection

Updated: 2026-10-18, Europe/Istanbul.

## Observed setup

On October 17 the owner-authorized Google setup created a test manager/child,
a dedicated Cloud project with Test API access, an External/Testing OAuth web
client and one test user. No campaign was created. The exact loopback callback was saved in Google on October 18;
no completed Google grant or Ads API read has been verified.

Client credentials are outside Git in the current Windows user's LocalAppData
`GrowthTwinsecrets/google-ads-oauth-client.dpapi`. They use user-scoped DPAPI.
The application's loader successfully decrypted/validated that client without
printing values. A separate fabricated payload passed encrypted write/read.
Do not relocate the file based on the previously attempted failed folder rename.

## Implemented local connection

Routes are present but disabled by default:

- `/connections/google/`: status and explicit start/disconnect forms.
- `/connections/google/start/`: authenticated, CSRF-protected POST.
- `/connections/google/callback/`: single-use state/PKCE validation, exchange
  at Google's fixed token endpoint and encrypted refresh-token storage.
- `/connections/google/disconnect/`: CSRF-protected POST; revoke before local
  deletion. Failed revocation retains the encrypted file for recovery.

The exact callback to register after local review is
`http://127.0.0.1:8002/connections/google/callback/`.
Google confirmed the redirect registration with “OAuth client saved”.

Runtime requires Windows, DEBUG false, host `127.0.0.1:8002`, loopback peer,
no forwarded headers, and all of these explicit environment settings:

- `GOOGLE_ADS_LOCAL_OAUTH_ENABLED=true`
- `GOOGLE_ADS_LOCAL_OWNER_ID`: disposable authenticated local user's ID
- `GOOGLE_ADS_LOCAL_WORKSPACE_ID`: workspace owned by that user

Use an isolated synthetic database and a single process without autoreload.
Never enable on staging, behind a proxy, or with multiple workers. A restart
invalidates pending five-minute challenges. Owner/workspace/session binding
and atomic in-process consumption prevent normal replay and cross-session use.
Credentials are bound to owner/workspace; do not repurpose those IDs or the
synthetic database without disconnecting and removing authorization first.

Google's adwords scope is broad, not read-only. This implementation has no Ads
API transport or publishing operation and does not verify an ad account as a
test target. Do not add Ads requests before verifying explicit test routing.
OAuth client configuration alone cannot establish actual account authorization.

No secrets are stored in sessions or returned to the browser. Google HTTP
redirects are rejected and token/revocation endpoints are fixed. Provider
errors are sanitized; failed storage attempts best-effort revocation. If that
also fails, remove the app permission through the Google account before retry.
A file's presence is only a local record, not proof the remote grant is valid.

Django callback-bearing console records are discarded; all connection responses
receive no-store; the form uses same-origin referrers so CSRF Origin checks work, while callbacks use no-referrer. This does not protect proxy/router logs or
arbitrary application logging. Do not turn DEBUG on for a live grant.

## Verification and next step

32 focused synthetic state, route and backend tests passed locally. Network and
storage were mocked in unit tests; the separate Windows checks above verified
only local encrypted storage. No real Google exchange/revocation was executed.

An isolated synthetic instance and disposable owner were opened on October 18. A real browser found Origin null caused by no-referrer on the form; the form policy was corrected without weakening CSRF, and Google account selection was reached. Phone identity verification is pending; no account grant completed.

Next: finish the owner identity verification and inspect the Google consent screen;
review the connection screen, then register the exact callback and obtain the
owner's Google account grant. Confirm encrypted save before the first explicitly
test-targeted read. Real advertising, media spend and beta launch remain gated.

## Current official guidance

Developer tokens were sunset; access is attached to the OAuth Cloud project.
Do not create a production manager merely to request a developer token.

- [Developer token migration](https://developers.google.com/google-ads/api/docs/api-policy/developer-token), checked October 17.
- [Web-server OAuth](https://developers.google.com/identity/protocols/oauth2/web-server), checked October 17.


## Verified authorization milestone — 2026-10-19

The owner completed identity verification and explicitly approved the displayed broad Ads scope. The live local callback exchanged the code and displayed encrypted save success and record present. This supersedes earlier statements above that a grant was pending. The fixed redirect is registered. The writer's executable-resolution failure was reproduced in the browser-launched environment and corrected; synthetic encrypted write/read then passed there. 35 focused tests passed. No Ads API account read or publication occurred. Preserve the current isolated database and owner/workspace IDs for the stored credential; do not recreate them under another identity. Next verify the explicit test customer's test_account flag using a read-only operation before any further account work.


## Verified test-account API read — 2026-10-19

A temporary local verifier refreshed the encrypted grant and queried only the designated test child via its designated manager, selecting customer ID, test flag and manager flag with LIMIT 1. Exactly one matching non-manager customer with testAccount=true was returned. No enumeration, campaign data, writes or spend occurred. This verifies authentication and the specific test target; it does not implement the reusable product adapter or establish live publication readiness.


## Application connection verification — 2026-10-19

The local UI now has a CSRF-protected test-account verification POST backed by the fixed read-only adapter. Set GOOGLE_ADS_LOCAL_TEST_CUSTOMER_ID and GOOGLE_ADS_LOCAL_TEST_MANAGER_ID explicitly; no target IDs are hard-coded or accepted from forms. The adapter refreshes the saved authorization and checks exactly one matching non-manager customer with testAccount=true. GET does not call Google. Successful evidence is session-local for at most ten minutes and bound to configured targets, owner/workspace and encrypted credential contents; failure/disconnect invalidates it. This recent observation is not continuous monitoring or campaign authorization. 47 focused tests and live browser verification passed; CI status must be checked on the current PR. No ad mutations or media spend.
