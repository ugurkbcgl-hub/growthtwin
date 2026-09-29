# ADR-0015: Authenticated campaign report without a data source

- Status: Accepted for local synthetic-data development only
- Date: 2026-09-29
- Decision owner: Project owner (delegated implementation decisions)

## Context

Workspace campaigns need a clear path to reporting, but they have no verified
advertising-platform connection or performance-data source. Displaying sample
or invented values could mislead an advertiser into treating them as actual
delivery, spend, engagement, or lead results.

## Decision

1. Provide a report page owned by each workspace campaign, showing the result
   categories that will be tracked: reach, impressions, clicks, other
   interactions, contact requests, and media spend.
2. Until a verified source is connected, show each category as unavailable and
   explain why. Show source and last-update status explicitly.
3. Do not substitute simulated figures, forecasts, or guarantees into this
   authenticated report page. Keep the separate public prototype sample report
   clearly identified as simulated.
4. Keep report access owner-scoped. Do not connect an ad platform, import
   account data, publish an ad, or spend money as part of this slice.

## Consequences

- Owners can find the report area and understand what data will appear there.
- The interface sets no expectation that the current application has live
  reporting or can guarantee campaign outcomes.
- Verified platform integration, source attribution, freshness, metric
  definitions, and campaign performance remain future work.
