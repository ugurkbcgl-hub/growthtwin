# ADR-0010: Synthetic action policy contract

- Status: Accepted for local synthetic-data development only
- Date: 2026-09-29
- Decision owner: Project owner (delegated implementation decisions)

## Context

Workspace campaign drafts are owner-scoped and carry a media cap, currency, and
flight dates. The `approvals` package has no policy implementation, however;
there is no deterministic check for authorization, destination, channel,
content, current policy state, stop requests, campaign spend, aggregate spend,
or schedule. A future publishing adapter must never infer permission from a
campaign's existence or an AI output.

## Decision

1. Add a pure, immutable evidence value and evaluator in `approvals`. Unknown
   consent/policy/stop facts, invalid money inputs, missing timestamps, or
   invalid bounds produce stable blocking reason codes.
2. Check campaign spend and aggregate account spend independently, in integer
   minor units of one explicit currency. The requested action must fall inside
   the campaign's timezone-aware flight interval.
3. Name the result `eligible_for_synthetic_review`. Even a result with no
   blocking reasons always has `live_dispatch_authorized = false`.
4. Keep the evaluator disconnected from views, persistence, providers, tokens,
   and publishing. It compares caller-supplied evidence only; it does not
   authenticate that evidence, reserve spend atomically, or establish policy
   freshness. Live dispatch therefore still requires a separately designed,
   server-owned and transactionally enforced authorization boundary.
5. Keep all examples synthetic. Do not create accounts, call provider APIs,
   publish, or spend media budget.

## Consequences

- Future application work has a deterministic, testable vocabulary for
  fail-closed preconditions and user-readable blocking reasons.
- The contract is not a complete safe-publishing system, legal review,
  account approval, or permission to process real advertiser data.
- Evidence provenance, consent versioning, current platform state, concurrent
  spend reservations, audit persistence, revocation and emergency-stop
  propagation remain open work before any live adapter is considered.

