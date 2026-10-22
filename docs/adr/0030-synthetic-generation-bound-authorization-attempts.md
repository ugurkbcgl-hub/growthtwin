# ADR-0030: Generation-bound synthetic authorization attempts

Status: Accepted for isolated synthetic rehearsal only
Date: 2026-10-22

## Decision

Add a default-off internal coordinator over ADR0029 identities. The constant
SYNTHETIC_CONNECTOR_AUTHORIZATION_ENABLED remains False in normal settings and
is explicitly overridden in isolated tests. There is no environment toggle, URL,
admin action or link to current Google runtime. Neither begin nor accepted fake
results opens the quarantined connection or grants provider-work permission.

An attempt contains only UUID/generation/revision, mode=synthetic, one of two
fixed typed scenarios, pending/running/accepted/rejected/expired status, an
allowlisted reason and timestamps. No OAuth state/code, PKCE, session, account ID,
token, credential handle or submitted evidence is accepted. Internal explicit
boolean confirmation and current active ownership are required. The lifetime is
exactly10 minutes; exact begin replay never extends it or changes the scenario.
A partial DB uniqueness constraint permits one active attempt per connection.
New begins cannot replace a current unexpired attempt; stale/expired attempts
are retired atomically before a new explicitly requested example is created.

Service paths lock owned workspace, connection, then attempt. Pending-to-running
reservation commits before invoking the deterministic local fake. The fake runs
outside transactions; calling perform inside an outer transaction is rejected.
Final acceptance reacquires locks and checks active ownership, current registry
state/generation/revision, switch, lifetime and immutable attempt binding again.
Accepted metadata requires ALLOW and an aware completion within its lifetime;
a contradictory fake outcome is failure. Corrupt histories or attempt metadata
fail closed. Historical read returns stored metadata, never current permission.

Duplicate running or terminal perform returns existing metadata without executing
the fake again. Crash/failed persistence after running leaves that receipt running;
there is no automatic resume. Explicit handling after expiry can mark it expired.
A concurrent block/rotation/expiry/disable cannot accept a late fake success.
Disabling/losing ownership may deny further service access; no grant write occurs.
Existing terminal history is not retroactively converted into current consent.

## Evidence and limits

23 new local tests and2 PostgreSQL-only races plus identity tests give38 local
passes and4 PostgreSQL skips. Required CI must verify the races. A review finding
about corrupt accepted metadata was fixed with regressions and independently
rechecked. Ruff/format and migration drift passed. Migration0004 creates only a
new table/constraints in ephemeral test DBs; no data migration or UI/browser work.

No actual Google OAuth, existing DPAPI grant, immutable dispatch ledger, provider,
fixture DB, Heroku or runtime hook is read, changed or protected by this rehearsal.
No token exchange, refresh, actual callback authenticity, production secret vault,
durable external no-resend barrier or remote exactly-once is demonstrated. ORM
writes can bypass service assumptions; these receipts are not independent recovery
proof. Real stop/reconcile must remain separately permitted in later integration.

Next: review the current Google TEST credential envelope and callback adoption/
rollback plan from source, then implement a default-off adapter boundary with
mocked pre/post exchange/result checks and explicit identity/generation binding.
Do not read/migrate/reactivate/reset the preserved grant while preparing it.
Actual account/permission or secret migration requires its applicable gates.
