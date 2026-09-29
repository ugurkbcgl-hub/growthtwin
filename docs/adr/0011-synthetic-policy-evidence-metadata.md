# ADR-0011: Synthetic policy-evidence metadata

- Status: Accepted for local synthetic-data development only
- Date: 2026-09-29
- Decision owner: Project owner (delegated implementation decisions)

## Context

[ADR-0010](0010-synthetic-action-policy-contract.md) defines a pure action-policy
check for synthetic previews. Its result currently does not carry where its
caller-supplied facts claim to come from or when they claim to have been
observed. Those details help a reviewer understand a result, but they cannot
prove origin or freshness.

## Decision

1. Add a small allowlist of synthetic evidence-source labels: `fixed_sample`
   and `test_fixture`. Missing, unknown, or non-enum values block synthetic
   review.
2. Require an observation timestamp that is timezone-aware. Missing or naive
   timestamps block review.
3. Echo valid source and observation-time claims in the returned decision so a
   future explanation can display them. The caller supplies both fields; the
   evaluator does not authenticate the source, capture the time, or prove the
   timestamp is accurate.
4. Set no freshness threshold and do not compare the timestamp with a clock.
   An old timestamp can pass this metadata check and must not be described as
   fresh.
5. Keep the metadata in memory only. Do not add persistence, external source
   connections, real-account data, or dispatch authorization.

## Consequences

- Synthetic policy results become easier to explain and test without implying
  trust in their provenance.
- Valid metadata never enables live dispatch; `live_dispatch_authorized`
  remains false.
- Trusted provider/workspace evidence, freshness policy, versioned policy
  snapshots, durable audit, and transactional budget reservations remain
  separate readiness work.

