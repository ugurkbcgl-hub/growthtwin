# ADR-0035: Explicit RESERVED candidate retirement with generation fencing

Status: Accepted for default-off mocked service validation only; no rollout
Date: 2026-10-22

Follow-up: ADR0036 adds separate closed scoped endpoints and a distinct fixed
callback URI, validated only with mocks. Earlier no-endpoint statements describe
this original slice; normal flags remain off and no actual rollout is claimed.

## Decision

Add an unwired metadata-only service behind the existing strict scoped-candidate
flag (normal False). Require active owned workspace, typed request/attempt/scope
UUIDs and revision, and explicit boolean retirement confirmation. No URL, client,
credential path/read/write, provider call, process-store cleanup or runtime change.

Lock workspace, connector and attempt in existing callback order. Only a consistent
RESERVED receipt matching the CURRENT quarantined generation/revision may retire.
Other unresolved history blocks retirement. EXCHANGING, UNCERTAIN, CANDIDATE and
other REJECTED receipts cannot be retired by this operation; blocked/stale scope
also denies. Lost session or expired handshake does not itself disqualify RESERVED,
because the adapter commits EXCHANGING before transport. This proves only a local
reservation boundary under this adapter, not remote revocation or grant absence.

In ONE outer SQL transaction, append the permanent generation-rotation receipt and
change the original attempt to REJECTED/retired_before_exchange. Add nullable unique
retirement_request_id and retired_generation metadata, with a DB constraint tying
both to that outcome. Metadata validation verifies the exact same-connector request,
replacement generation, original generation/revision and next ordinal receipt.
Conditional attempt update and final validation must succeed or rotation rolls back.
Original attempt identity, timestamps and history remain unchanged.

Exact request replay validates that durable binding and returns CURRENT identity,
including later rotation/block, without further writes or reopening anything. A
different request or conflicting connector/rotation identity is rejected. A later
authorization must use a distinct attempt and the new current generation; it still
passes all existing legacy/client/scope gates. Retirement grants no provider-work
permission. The stale process-local nonce may remain until expiry: terminal receipt
and generation checks, not deletion of process memory, fence its callback.

## Races, evidence and limits

If callback commits EXCHANGING first, retirement must deny while the mocked outbound
request completes. If retirement commits first, callback observes REJECTED and sends
zero transport requests. Neither branch automatically revokes, unlinks, retries,
activates or adopts credentials. Legacy grant and separately permitted stop/reconcile
paths remain unchanged. This does not solve orphan reconciliation or backup restore.

14 new local tests and2 PostgreSQL races. With existing candidate adapter/recovery:
42 local passes,4 PostgreSQL skips. Tests cover permanent replay after later block,
new-generation start, all non-reserved states, confirmation/default-off, ownership,
request collision across connectors, corrupt receipt and atomic rollback after
rotation. All client/path/transport/read/write boundaries mocked; no actual secrets,
provider, preserved DB, browser fixture or Heroku operation. Migration0006 applies
only in ephemeral test DBs for this slice. No manual browser check for service-only
work. Independent final source review found no blocker; required CI verifies races.

Next: separate scoped start/callback/retirement endpoint wiring with session/CSRF
and mocked transport tests, keeping normal runtime off. Configured TEST target
proof, orphan reconciliation, explicit legacy adoption/rollback, scoped refresh
and production privacy/access/recovery/financial gates remain open.
