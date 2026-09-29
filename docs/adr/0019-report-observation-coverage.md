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
4. Freshness is computed by a pure classifier from the source's
   `source_data_as_of` timestamp, the timezone-aware evaluation time, and a
   configured `MetricFreshnessRule` that names its source, metric family,
   identifier, and positive maximum age. At the exact maximum age data is
   `current`; older data is `stale`. Missing rule/source time and a source time
   later than the evaluation time produce `unknown`. Retrieval time is not an
   input to this classification. The observation and metric must match the
   rule's source and metric family. The configured age is application policy,
   not a provider SLO or guarantee.
5. A partial unavailable metric must carry an observation that is not complete
   for its period. A stale unavailable metric carries a complete last
   observation and a rule evaluation that classifies it as stale.
6. Observation scope, completion flags, source timestamps, and rule identity are
   caller-supplied evidence. They are useful for deterministic contracts and
   synthetic tests, but do not authenticate a provider, account, query,
   pagination, row, source timestamp, or data source. No live adapter is
   included.

## Consequences

- Retrieval time is distinct from the report period and coverage.
- A source adapter must prove scope, row presence, full period coverage, and
  complete retrieval before returning an available value.
- Freshness evaluation is deterministic once a source/metric policy is
  explicitly configured. Choosing production thresholds remains metric/source-
  specific and must be reviewed against current source guidance. No database
  schema, provider adapter, account connection,
  real-data import, publication, or spend is included.
