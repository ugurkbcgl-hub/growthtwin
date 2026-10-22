# ADR-0036: Closed scoped TEST endpoint wiring

Status: Accepted for mocked request validation only; not enabled or rolled out
Date: 2026-10-22

## Routing and gates

New `/connections/google/scoped/` overview/start/callback/retire routes call the
candidate and retirement services. Both endpoint and candidate flags remain False,
without environment toggles. Existing local OAuth flag and exact configured active
owner/workspace, DEBUG False, Host127.0.0.1:8002, remote loopback and no-forwarded
guards also apply. Unauthorized callback never redirects to login. No normal
campaign navigation link, actual activation or live endpoint invocation in tools.

Separate fixed redirect URI:
`http://127.0.0.1:8002/connections/google/scoped/callback/`.
The store accepts ONLY its original legacy URI and this exact new URI, defaulting
to legacy. Candidate authorization and token exchange both use the new URI;
legacy views/store/redirect/grant consumers remain unchanged. This slice did not
inspect or change Google client configuration. New redirect registration/current
TEST target proof must be verified before enabling; no claim of actual OAuth success.
Process-local PKCE/state still requires the same process; multiworker/restart
recovery is not implemented and cannot infer permission to retry outbound work.

## Request boundaries

Overview GET reads owned metadata only, not credentials/path/provider. Start and
retire require CSRF, explicit confirmation, exact single-value fields and signed
five-minute owner/workspace/session-HMAC/connection/generation/revision/attempt/
action tickets. Retirement also binds request UUID and immutable receipt digest.
The service verifies that digest UNDER workspace/connector/attempt locks before
replay or rotation, closing the independently found check/use race. Trusted
internal callers retain the prior optional-digest API; HTTP callers always supply
their signed expected digest. Current state/time/scope services remain authoritative.

After start, session stores metadata plus SHA256 OAuth-state digest, never raw
state/code/verifier, authorization URL or credentials. Callback requires that
marker, originating session, exact receipt scope and matching state hash BEFORE
calling consume. Missing/wrong/duplicate/old state does not burn a new reservation.
The service still validates state/PKCE/code and commits EXCHANGING before transport.
Terminal callback replay cannot send twice. All processed/invalid allowed callbacks
303 to a clean local status URL; notices are fixed non-sensitive enums. A slashless
alias avoids a framework redirect carrying the query. Both aliases have no-referrer.

Retirement only clears a matching old marker; replay cannot erase a newer attempt's
marker. Fresh session may explicitly retire an owned unexchanged reservation but
cannot rebind/consume the old handshake. Other states have no retirement control;
uncertainty prevents new starts. Candidate result is inactive, not target proof or
an active grant. No readback, refresh, create, revoke or adoption operation is added.

Private/no-store/noindex headers cover new-prefix framework/CSRF errors. Form pages
use same-origin referrer for CSRF; callback uses no-referrer. Django callback filter
drops both callback paths, decoded/encoded, including record exceptions/request
extras. External proxy/router/access-log and error-reporting controls remain a
separate enabling gate; this is not a generic secret filter.

## Evidence and next action

25 new request tests; with existing adapter/retirement/legacy store/view tests:
76 local passes,4 PostgreSQL skips. Real client/path/transport/encrypted I/O mocked.
Coverage includes both closed flags, loopback/owner/CSRF, signed scope/session/
expiry/action, state routing/replay, rotated session, inactive result, uncertainty,
legacy-presence denial, immutable receipt drift between view read/service lock,
slashless cleansing and legacy redirect preservation. Independent final review
approved after the digest check moved under the lock. Ruff/format/migration drift
and whitespace passed. No new migration, actual provider/credential/preserved DB/
Heroku operation or deployment. No manual browser review: request-level validation
only; exact loopback8002 and normal closed flags were not relaxed for a preview.

Next: verify isolated TEST OAuth configuration/new redirect and current target
readiness before enabling a separately authorized candidate exercise. Preserve
legacy grant/ledgers; no publishing, account upgrade, candidate adoption, refresh
or actual credential cleanup. Orphan reconciliation, legacy adoption/rollback,
production vault/access/privacy/recovery/financial gates remain open.
