# GrowthTwin — current handoff

Last verified: 2026-09-29 20:28 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `98048ec` after PR #145. Required PR CI `36604492004` and post-merge main CI `36604748472` passed.
- Current branch: `docs/report-completeness-handoff`, based on `main`; it reconciles project status references with the merged PR #145 research. Its PR has not yet been opened.
- PR #143 focused local verification passed: 41 campaign Django tests, Django system check, migration consistency, Ruff lint/format, and diff checks. Browser E2E passed in PR CI; local browser E2E was not run because pytest is absent locally.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability reference, not first-release scope.
- Local synthetic-data product development is authorized. Staging E2E, backup/restore, rollback, and other release-readiness gates remain before external beta or production.
- PR #135 added the authenticated report shell; #138 established a provider-neutral typed metric contract; #140 connected typed unavailable metrics and labeled dates as the planned campaign period; #141 defined provider-neutral metric semantics; #142 mapped official Google Ads API v25 fields for the Search candidate; #143 added typed unavailable reasons and metric-level Turkish explanations; #145 documented Google Ads Search zero-row completeness and metric-family freshness behavior.
- Google Ads may omit date rows with no metrics and segmented rows where all selected metrics are zero. Update guidance differs by metric family and data may be adjusted later. A report fetch time does not prove underlying completeness or freshness. No evaluator, adapter, account connection, or real data is implemented.
- Only an `available` metric with numeric zero represents a source-confirmed zero. The authenticated report remains disconnected and contains no observed values. Search mapping leaves reach unavailable; text-ad interactions are not added again to clicks; attributed conversions do not prove delivered leads.
- Keep the Django/PostgreSQL modular monolith and previously approved Heroku staging only. No additional paid service. Real advertiser/customer/lead data, uploads, production AI, platform account connections, publication, advertiser spend, and payments remain out of scope. Never push directly to `main`; successful PRs may be merged after review and required CI under the owner's standing authorization.

## Open risks

- Real-data readiness and release gates remain: secure file handling, privacy/retention, data recipients, provider terms, Türkiye-specific platform/API approvals, token protection/revocation, audit/stop behavior, backup/restore, rollback, and staging browser E2E.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- Google Ads API access/eligibility remains unverified. Source-specific completeness/freshness validation, ingestion, and durable audit are not implemented.

## Next action

Merge this status-document update after required CI passes, then implement and test a provider-free observation/coverage contract so an absent row or fetch timestamp alone cannot imply a complete, fresh zero.
