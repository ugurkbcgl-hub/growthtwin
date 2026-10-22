# ADR-0038: Synthetic inspection recovery executor

Status: Accepted for fixed-fixture rehearsal only; actual readback remains unwired
Date: 2026-10-22

## Scope

ADR0037 introduced an irreversible metadata-only permit claim. This slice tests
how a future executor must use that claim and reject changes during an inspection.
It does not turn the metadata snapshot into a bearer capability or enable the
existing origin-session reader.

The new service is gated by both the existing recovery switch and a new
GOOGLE_ADS_INSPECTION_REHEARSAL_ENABLED switch, each strictly True and default
False without an environment toggle. No route or deployment is added. The API
accepts owned scope, a server-session string and one of five fixed scenario names;
it accepts no reader callback, storage adapter, path, envelope or permit snapshot.

Only a receipt with the hash of the fixed fabricated inspection client is eligible.
That guard runs before consumption, so an actual configured Google client receipt
cannot use this rehearsal. Metadata is fabricated directly in ephemeral tests;
no actual candidate database is opened or migrated.

## Claim and checks

Admission uses the existing workspace -> connector -> attempt -> permit lock
order and checks active ownership, current quarantined CANDIDATE, receipt digest,
new-session HMAC, exact permit duration and unexpired ISSUED state. The executor
calls consume_inspection_permit directly; only that function's internal return is
accepted as the claim. The claim commits before any fixture probe runs. A caller
transaction is rejected.

After claim, immediately before the simulated read, and after the probe completes,
the service reloads and locks current metadata. It recomputes the current session
HMAC, checks the original immutable receipt digest, exact consumed snapshot and
initial creation/deadline, and requires consumed_at <= now < expires_at. Inactive
or transferred ownership, rotation/block, receipt/permit tampering, switch or
SECRET_KEY change, expiry and clock movement before creation/consumption fail
closed. Smaller clock changes within that interval are not detected; no monotonic
elapsed-time guarantee is claimed. No original receipt, identity or generation
is rewritten.

Fixture client and legacy-presence checks run before and after the simulated read,
outside database locks. Exact typed booleans and bounded hashes are required.
Malformed envelope or simulated failures produce a bounded negative disposition;
post-operation metadata checks still run before returning. A successful fixture
envelope uses the existing strict binding codec, but only the explicit
synthetic_match label can be returned. No token, envelope, hash, path or raw session
is returned. Result fields are frozen request/attempt IDs and disposition only.

## Fixed in-memory boundary

The internal probe has deterministic match, legacy_exists, client_changed,
invalid_envelope and unreadable scenarios. Its exact address contains the owned
fixture connection/attempt/generation; it is not a filesystem path. It imports
no backend, filesystem or transport adapter and cannot read legacy contents.
The client/legacy checks are **simulations**, not evidence about current Google
configuration or encrypted storage. Tests may replace internal probe behavior
to introduce drift and race timing; application callers cannot supply such a hook.

CONSUMED remains only a terminal claim. No result is persisted and failure/crash
cannot reopen, renew or replace the one-per-candidate permit. No automatic retry,
uncertainty reconciliation, real reader, refresh, account proof, grant adoption,
activation, revoke or advertising is implemented. Original readback stays unchanged.

## Remaining gates

A separately designed actual recovery reader needs trusted configured-client and
legacy-location binding independent of a lost origin session, an exact candidate
path, bounded encrypted I/O, repeated client/legacy/scope/time checks, and explicit
failure/uncertainty handling. The fixture address and synthetic_match cannot satisfy
those requirements. The current local backend derives its durable legacy path
from configured owner/workspace IDs (the session binds the handshake, not that
path). A future adapter must verify that mapping and preserve the same location;
it must not infer absence from a newly invented session-specific path. No
production vault/restart recovery guarantee is implied.

Before exposing recovery to a browser, derive identity/session on the server and
add authenticated ownership, CSRF, signed scope/action consent and safe result
handling. Actual candidate access remains a separate reviewed operation, with
normal switches off and preserved credentials/databases untouched.

## Validation

Focused service tests cover irreversible claims, fixture-only/no-I/O admission,
negative outcomes, immutable metadata, post-read drift and safe results. PostgreSQL
CI supplies row-lock concurrency evidence. Executed counts and PR/merge outcomes
are recorded in TESTING.md, STATE.md and the PR; no UI change requires a new browser
rehearsal in this slice.
