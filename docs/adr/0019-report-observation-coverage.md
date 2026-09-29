# ADR-0019: Report observation coverage and retrieval metadata

- Status: Accepted for local synthetic-data development only
- Date: 2026-09-29
- Decision owner: Project owner (delegated implementation decisions)

## Context

ADR-0016 requires a source and observation timestamp, while ADR-0018 uses
partial and stale unavailable reasons. A single timestamp does not say whether
the requested report period was observed. Provider guidance also documents
that report rows can be omitted, including segmented all-zero rows. Treating an
omitted row or a recent fetch as a confirmed zero could fabricate a result.

## Decision

1. Model an observation as immutable metadata with an explicit report scope,
   requested period, covered period, timezone-aware retrieval time, successful
   response/pagination completion, whether the metric row was present, and a
   freshness classification (`current`, `stale`, or `unknown`) with a named
   source-specific freshness rule for `current` or `stale`.
2. A metric observation is complete for its requested period only when the
   requested and metric windows match exactly, the covered period equals that
   window, retrieval completed successfully, and the metric row was present.
3. An available metric, including a numeric zero, requires a complete
   observation for the exact period and `current` freshness under a named
   source-specific rule. A missing row cannot be mapped to zero, even if the
   report request completed and its fetch time is recent. `unknown` freshness
   must remain unavailable.
4. A partial unavailable metric must carry an observation that is not complete
   for its period. A stale unavailable metric carries a complete last
   observation and a source-specific rule that classifies it as stale. This
   type adds no universal age threshold and does not itself compute freshness.
5. Observation scope, completion flags, and freshness-rule labels are
   caller-supplied evidence. They are useful for deterministic contracts and
   synthetic tests, but do not authenticate a provider, account, query,
   pagination, row, freshness calculation, or data source.

## Consequences

- Retrieval time is distinct from the report period and coverage.
- A source adapter must prove scope, row presence, full period coverage, and
  complete retrieval before returning an available value.
- Freshness remains metric/source-specific and must be reviewed against current
  source guidance. No database schema, provider adapter, account connection,
  real-data import, publication, or spend is included.
