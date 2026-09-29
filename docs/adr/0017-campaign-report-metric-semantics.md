# ADR-0017: Provider-neutral campaign report metric semantics

- Status: Accepted for local design and synthetic-data development only
- Date: 2026-09-29
- Decision owner: Project owner (delegated implementation decisions)

## Context

ADR-0016 gives report values a typed unavailable/available state, reporting
window, unit/currency, source, and observation time. The six labels in the
current report still need consistent meanings before a channel adapter can map
provider data to them. Similar-looking platform metrics can differ in their
event, identity, deduplication, timezone, and attribution rules.

## Decision

1. **Reach** means a source-reported unique audience for its stated identity
   and scope. Keep the source's scope visible; do not add reach across platforms
   or assume it is deduplicated across campaigns.
2. **Impressions** means source-reported ad deliveries under that source's
   definition. It is not unique audience and cannot be inferred from reach.
3. **Clicks** means clicks directed to the campaign destination when the
   source provides that measure. Keep other click types separate; do not
   silently equate all interactions with destination clicks.
4. **Other interactions** are source-defined engagement events other than the
   selected destination-click measure. Preserve event subtype; any aggregate
   must list its included event types and must not imply cross-platform
   equivalence.
5. **Contact requests** are distinct, actually received request records (for
   example a delivered lead-form record), counted under an explicit
   deduplication rule. An ad conversion event alone is not proof that a request
   was delivered or qualified.
6. **Media spend** is source-reported media cost for the reporting window. It
   is distinct from the planned budget, GrowthTwin fees, tax, and FX. Preserve
   the ad-account currency; do not combine currencies without a separately
   evidenced conversion and disclosed method.
7. Interpret report dates in the connected ad account's configured timezone.
   Do not silently use the viewer's browser timezone. Preserve the source's
   attribution model/window for outcomes; show observed delivery separately
   from attributed outcomes. Do not claim cross-source comparability where
   definitions differ.
8. A value is available only for a source-confirmed observation of the stated
   metric and period. Zero is valid only when the source confirms complete
   observation of that period. Missing, partial, delayed, or stale results
   remain unavailable/stale; never convert them to zero. Forecasts and
   simulations remain separate from observed results.
9. Freshness thresholds and completeness rules are source-specific and must be
   verified before integration. There is no universal freshness duration.
   The contract/UI must expose incomplete or stale data before any live report
   can imply that a period is final.

## Consequences

- The current authenticated report shell remains unavailable until a verified
  source exists. Its displayed dates are explicitly the **planned campaign
  period**, not proof that delivery occurred in that period.
- A future adapter must map native source definitions and preserve attribution,
  timezone, completeness, and freshness metadata instead of flattening them
  into unsupported universal totals.
- No platform connection, real-data import, legal conclusion, ad publishing, or
  spend is authorized by this semantic decision. Platform-specific mappings
  require current primary-source research and separate readiness checks.
