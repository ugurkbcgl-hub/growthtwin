# ADR-0016: Provider-neutral campaign report metric contract

- Status: Accepted for local synthetic-data development only
- Date: 2026-09-29
- Decision owner: Project owner (delegated implementation decisions)

## Context

ADR-0015 established an authenticated report shell, but the report has no
verified channel source. A future integration needs an explicit distinction
between an observed zero and a metric that could not be observed. It also needs
the reporting period, unit/currency, data source, and observation time so a
number is interpretable and traceable.

## Decision

1. Define a provider-neutral, immutable Python value for one campaign metric.
2. Require an explicit available/unavailable status. Available values may be
   zero, must be non-negative and finite, and require an inclusive reporting
   window, a source, and timezone-aware observation timestamp. Unavailable
   metrics carry no value or observed-data provenance; their window is included
   when one is known, and omitted if the campaign has no defined flight dates.
3. Distinguish count and currency units. Currency metrics require a three-letter
   uppercase code; count metrics cannot carry a currency.
4. Keep this contract persistence-free and disconnected from the report UI.
   Tests use synthetic fixtures only. This decision does not authorize platform
   connections, importing real data, account access, publication, or spend.

## Consequences

- Integrations can map provider results into a shared, testable shape without
  coupling the domain contract to a specific platform.
- Consumers must handle unavailable data separately from a real zero and must
  not infer a reporting period where none was defined.
- Metric meaning, attribution, source trust, freshness thresholds, ingestion,
  and durable audit remain to be specified before real reporting is enabled.
