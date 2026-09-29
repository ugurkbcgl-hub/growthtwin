# GrowthTwin — current handoff

Last verified: 2026-09-29 21:57 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `efce64f` after PR #147. Its required CI `36606129893` and post-merge CI `36606390578` passed.
- Current branch: `feat/report-observation-coverage`, based on `main`; implementation, tests, ADR-0019, and status-document updates are in progress. PR not yet opened.
- Local checks for this slice: 46 campaign Django tests passed; Django system check and migration consistency passed; Ruff lint/format passed. Browser E2E not run locally because pytest is absent; required PR CI remains pending.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability reference, not first-release scope.
- Local synthetic-data product development is authorized. Staging E2E, backup/restore, rollback, and other release-readiness gates remain before external beta or production.
- PR #135 added the authenticated report shell; #138 established a provider-neutral typed metric contract; #140 connected typed unavailable metrics and labeled dates as the planned campaign period; #141 defined provider-neutral metric semantics; #142 mapped official Google Ads API v25 fields; #143 added typed unavailable reasons; #145 documented source-specific zero-row and freshness behavior; #147 refreshed the handoff.
- Current feature adds `MetricObservation`: exact requested/covered period, scope, retrieval time, completed response, row presence, freshness result and named rule. A metric can be available only with a complete exact-period row and `current` freshness under a named source-specific rule. An absent row or recent fetch alone cannot confirm zero. The status is caller-supplied contract evidence, not authentication, a freshness evaluator, or a provider integration.
- The authenticated report remains disconnected and contains no observed values. Search mapping leaves reach unavailable; text-ad interactions are not added again to clicks; attributed conversions do not prove delivered leads.
- Keep the Django/PostgreSQL modular monolith and previously approved Heroku staging only. No additional paid service. Real advertiser/customer/lead data, uploads, production AI, platform account connections, publication, advertiser spend, and payments remain out of scope. Never push directly to `main`; successful PRs may be merged after review and required CI under the owner's standing authorization.

## Open risks

- Real-data readiness and release gates remain: secure file handling, privacy/retention, data recipients, provider terms, Türkiye-specific platform/API approvals, token protection/revocation, audit/stop behavior, backup/restore, rollback, and staging browser E2E.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- Google Ads API access/eligibility remains unverified. No freshness thresholds are computed; provider-specific adapters, source verification, ingestion, and durable audit are not implemented.

## Next action

Open a PR for the observation/coverage contract, review the diff, and merge only after required CI succeeds. Then define and test source-specific freshness rule evaluation with synthetic timestamps; do not treat platform SLOs as guarantees or add a live adapter.
