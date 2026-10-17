# Google Ads test integration prerequisites

Reviewed: 2026-10-17, Europe/Istanbul. Setup is partly complete; no API
connection, publication or media spend has been verified.

## Verified setup

During the owner-authorized browser setup on October 17:

- Dedicated test manager and child were created; the child overview showed
  zero campaigns. Account identifiers are deliberately omitted here.
- Dedicated Cloud project was created with owner-approved billing association;
  Google Ads API was enabled and its access page displayed Test access.
- OAuth branding is External / Testing. One web client exists and the owner's
  signed-in account was added as the single test user.
- Client credentials were saved outside Git with Windows user-scoped DPAPI;
  encryption/decryption round-trip succeeded in the writer process. A later
  folder rename failed with an access error. Runtime access from Django has
  NOT been established; confirm store location/identity before loading.
- Authorized redirect URIs and JavaScript origins remain empty. No OAuth grant,
  refresh token, test-account API read or provider adapter has been verified.

These are dated setup observations, not proof that the application is connected.
Do not record private IDs, email addresses or credential values in this repository.

## Corrected API access prerequisite

Google's current developer-token migration guide says developer tokens were
sunset on September 9, 2026. Access is now attached to the Cloud project owning
OAuth credentials. Do not create a production manager just to obtain a token.
The previous checklist's developer-token prerequisite is superseded. Recheck
Cloud access before calls; Test access does not authorize production targets.

## Implemented offline foundation

`growthtwin.modules.connections.google_oauth` prepares a fixed Google consent
URL with PKCE S256 and a five-minute random state. An in-memory lock consumes
an attempt once, bound to server-supplied owner, workspace and session values.
There is one attempt per binding and a 100-entry cap; restart invalidates all
attempts. It is only suitable for a single isolated local process.

Proposed local callback: `http://127.0.0.1:8002/connections/google/callback/`.
This is a constant for future integration, NOT an installed Django route or a
registered Google redirect URI. No network or credential operation is performed.
The adwords OAuth scope is broad; it must not be described as read-only.

Django console handlers now discard records mentioning this callback path,
including slashless/encoded requests and exception records with this request
path. This does not protect proxy/router logs, arbitrary application loggers,
provider response bodies, or DEBUG exception pages.

## Next implementation gate

1. Implement authenticated, CSRF-protected start and dedicated callback routes,
   enforce workspace ownership and isolated loopback-only operation with DEBUG
   disabled. Never redirect an unauthenticated callback to a secret-bearing
   login `next` URL. Return clean status redirects with no-store/no-referrer.
2. Establish a credential-store interface and verify encrypted runtime access,
   token storage, sanitized failures and disconnect/revocation. Do not store
   tokens or PKCE verifiers in plaintext Django sessions.
3. Register the exact implemented redirect URI and request the owner's Google
   account grant. Verify test-only customer routing before the first narrow
   read; do not enumerate unrelated advertiser data.
4. Verify test-account status through the API before a separately reviewed
   paused synthetic campaign creation/stop rehearsal. Live serving, meaningful
   metrics, real advertiser data and media spend remain separate release gates.

## Official references

- [Developer token migration](https://developers.google.com/google-ads/api/docs/api-policy/developer-token), checked 2026-10-17; main guide supersedes its stale summary box.
- [Web-server OAuth](https://developers.google.com/identity/protocols/oauth2/web-server), checked 2026-10-17.
- [Test accounts](https://developers.google.com/google-ads/api/docs/best-practices/test-accounts), earlier review 2026-10-16.
