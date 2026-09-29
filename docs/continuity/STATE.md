# GrowthTwin — current handoff

Last verified: 2026-09-29 19:55 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Main is `ac70347bb95dcf171ae2ec9e873eeffbfe903426` after PR #141. Required CI `36600578303` and post-merge CI `36600848130` passed.
- Current branch `docs/google-search-report-metric-mapping` holds official-source mapping research and synchronized project/handoff docs. Its PR has not yet been opened; verify live Git/PR state before assuming a PR number.
- PR #141's focused local checks passed: 38 campaign tests, 3 authenticated browser E2E tests, Django system and migration checks, Ruff lint/format, and whitespace checks. CI passed.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability reference, not first-release scope.
- Local synthetic-data product development is authorized. Staging E2E, backup/restore, rollback, and other release-readiness gates remain before external beta or production.
- PR #135 added the authenticated report shell; PR #138 defined the provider-neutral typed metric contract; PR #140 connected typed unavailable metrics and labels displayed dates as the **planned campaign period**; PR #141 defined provider-neutral metric semantics. The report still has no verified source or observed values.
- Official Google Ads API v25 research for the first Search workflow (in the current documentation branch) indicates: Search does not have documented `unique_users` reach support; `interactions` for text ads describes clicks, so it should not be added as a separate count; conversion events do not prove lead delivery; and conversion data may lag, with zero-only rows omitted. No API request, account access, or real data was used. See the mapping document in the current branch and [ADR-0017](../adr/0017-campaign-report-metric-semantics.md).
- Keep the Django/PostgreSQL modular monolith and previously approved Heroku staging only. No additional paid service. Real advertiser/customer/lead data, uploads, production AI, platform account connections, publication, advertiser spend, and payments remain out of scope. Never push directly to `main`; successful PRs may be merged after review and required CI under the owner's standing authorization.

## Open risks

- Real-data readiness and release gates remain: secure file handling, privacy/retention, data recipients, provider terms, Türkiye-specific platform/API approvals, token protection/revocation, audit/stop behavior, backup/restore, rollback, and staging browser E2E.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- API approval/access level and account eligibility are unverified. Metric mappings, source provenance, freshness/completeness, attribution settings, ingestion, and durable audit are not implemented.

## Next action

After updating and merging the official-source mapping, design the report's explicit unavailable reasons (`not connected`, `unsupported`, `partial`, `stale`) so they cannot be mistaken for a verified zero. Keep it provider-free and synthetic-only.
