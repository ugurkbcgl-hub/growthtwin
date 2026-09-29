# GrowthTwin — current handoff

Last verified: 2026-09-29 20:13 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `6764c9c` (PR #143, explicit unavailable report metric reasons). Required PR CI `36602784613` and post-merge CI `36603066285` passed.
- Current documentation branch: `docs/report-unavailable-reasons-handoff`, based on `main`. It updates verified status references after PR #143. Confirm open PR state before assuming this docs-only branch is submitted.
- PR #143 focused local verification passed: 41 campaign Django tests, Django system check, migration consistency, Ruff lint/format, and diff checks. Browser E2E ran and passed in PR CI; local browser E2E was not run because pytest is absent from the local environment.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability reference, not first-release scope.
- Local synthetic-data product development is authorized. Staging E2E, backup/restore, rollback, and other release-readiness gates remain before external beta or production.
- PR #135 added the authenticated report shell; #138 established a provider-neutral typed metric contract; #140 connected typed unavailable metrics and identified displayed dates as the planned campaign period; #141 defined provider-neutral metric semantics; #142 mapped official Google Ads API v25 fields for the Search candidate without account access or API requests; #143 added typed `not_connected`, `unsupported`, `partial`, and `stale` reasons with provenance rules and Turkish per-metric explanations.
- Only an `available` metric with numeric zero represents a source-confirmed zero. The authenticated report remains disconnected and contains no observed values. Search mapping leaves reach unavailable; text-ad interactions are not added again to clicks; attributed conversions do not prove delivered leads.
- Keep the Django/PostgreSQL modular monolith and previously approved Heroku staging only. No additional paid service. Real advertiser/customer/lead data, uploads, production AI, platform account connections, publication, advertiser spend, and payments remain out of scope. Never push directly to `main`; successful PRs may be merged after review and required CI under the owner's standing authorization.

## Open risks

- Real-data readiness and release gates remain: secure file handling, privacy/retention, data recipients, provider terms, Türkiye-specific platform/API approvals, token protection/revocation, audit/stop behavior, backup/restore, rollback, and staging browser E2E.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- Google Ads API access/eligibility remains unverified. Source-specific row completeness, zero-row omission, freshness, attribution settings, ingestion, and durable audit are not implemented.

## Next action

Define source-specific completeness and freshness rules for report metrics, starting with the documented Google Ads behavior that rows may be omitted when selected metrics are all zero. Keep this research/code slice synthetic and provider-free; do not add account access or a live adapter.
