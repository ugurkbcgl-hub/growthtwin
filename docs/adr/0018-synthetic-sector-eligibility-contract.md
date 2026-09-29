# ADR-0018: Synthetic sector and channel eligibility contract

- Status: Accepted for local synthetic-data development only
- Date: 2026-09-30
- Decision owner: Project owner (delegated implementation decisions)

## Context

The dated Google Search Türkiye matrix defines category/channel states and says
unknown or stale rules must pause. Existing synthetic action checks accept a
single `channel_allowed` boolean, which cannot represent sector rules, rule
sources, review dates, or the distinction between a restriction and a stop.

## Decision

1. Add a pure immutable contract under `approvals` with four outcomes:
   `eligible`, `restricted`, `not_supported`, and `needs_review`.
2. Each caller-supplied rule claim carries jurisdiction, channel, category,
   outcome, HTTPS source URL, rule version, review date, review-due date, and
   whether its conditions are satisfied. The caller supplies the evaluation
   date so results do not depend on a hidden system clock.
3. Missing/invalid metadata, expired review dates, unknown outcomes, and
   unsatisfied or unknown conditions fail closed to `needs_review`. When
   combining independent law/platform claims, `not_supported` takes precedence,
   then `needs_review`, then `restricted`, then `eligible`.
4. Keep the values and evaluation in memory. They are unverified caller claims;
   the evaluator does not retrieve sources, establish legal conclusions,
   authenticate advertiser evidence, prove rule freshness, persist an audit,
   connect accounts, or authorize dispatch.
5. Do not connect the contract to publication or a live channel. A later
   integration requires separate review, focused coverage, and an explicit
   server-owned authorization boundary.
6. The campaign-preview fixture uses a 30-day re-review date only to
   demonstrate the stale-rule transition. This is not a rule expiry, legal
   deadline, or platform-mandated review period.

## Consequences

- A local synthetic draft can represent category eligibility independently
  from action authorization and show why the result is restricted or paused.
- A missing or stale rule cannot become eligible because a caller omitted a
  field. The caller-supplied state still cannot prove the truth of the source
  or conditions.
- Persistence, source authentication, automatic policy updates, real-data
  handling, publication, and account/API access remain out of scope.
