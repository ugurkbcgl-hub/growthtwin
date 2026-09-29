# ADR-0018: Explicit unavailable report metric reasons

- Status: Accepted for local synthetic-data development only
- Date: 2026-09-29
- Decision owner: Project owner (delegated implementation decisions)

## Context

ADR-0016 distinguishes an observed zero from an unavailable report metric, but
one generic unavailable state cannot explain whether a source is disconnected,
the channel does not provide a metric, only part of a period was observed, or
the last observation is stale. The official Google Ads Search mapping also
identified metrics that are not available for the selected Search workflow.

## Decision

1. Keep metric status as `available` or `unavailable`. `available` with the
   numeric value zero remains the only representation of a source-confirmed
   zero.
2. Every unavailable metric must use one reason: `not_connected`, `unsupported`,
   `partial`, or `stale`. Unavailable values always carry no numeric value.
3. `not_connected` carries no source observation. `unsupported` identifies the
   channel/source, but has no observation timestamp. `partial` and `stale`
   require a source, a reporting window, and a timezone-aware observation time.
4. Display a plain-language explanation at the metric itself. Do not substitute
   an unavailable reason with zero, hide its source/period state, or describe a
   scheduled campaign period as observed delivery.
5. This is a provider-neutral, persistence-free contract. Any implemented
   source mapping still requires verified platform access, source completeness
   and freshness rules, user authorization, and separate readiness checks.

## Consequences

- The report can explain why a value is absent without pretending that all
  channels or time periods behave alike.
- Adapters must not mark a metric available until its source, period, and
  completeness are sufficient for a real value.
- This decision adds no provider, database migration, account connection,
  publication, advertiser spend, or real-data handling.
