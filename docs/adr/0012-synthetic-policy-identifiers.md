# ADR-0012: Synthetic policy version and rule identifiers

- Status: Accepted for local synthetic-data development only
- Date: 2026-09-29
- Decision owner: Project owner (delegated implementation decisions)

## Context

The synthetic action-policy result reports stable blocking reasons, but does
not identify the evaluator version or the set of deterministic checks it ran.
Those identifiers help explain and compare local synthetic results. They do not
make caller-supplied evidence trustworthy.

## Decision

1. Add a fixed `synthetic-action-policy.v1` identifier to every decision.
2. Report the stable allowlisted rule identifiers evaluated by this version,
   including for blocked decisions. Keep the identifiers in deterministic
   declaration order.
3. Keep the identifiers informational and in memory. They are not a signed
   policy snapshot, evidence authentication, persisted audit, or permission to
   dispatch.
4. Do not add persistence, live integrations, spend reservation, or external
   side effects.

## Consequences

- A future explanation can identify the local rule set associated with a
  synthetic decision.
- Changing the evaluator semantics requires an explicit new version decision;
  this contract alone does not preserve historical results.
- Trusted provenance, versioned durable audit, freshness, atomic budget
  reservation, and dispatch authorization remain separate readiness work.
