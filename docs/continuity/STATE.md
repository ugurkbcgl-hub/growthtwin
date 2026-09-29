# GrowthTwin — current handoff

Last verified: 2026-09-29 20:07 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `c454953` (PR #142, Google Search report metric mapping). Required CI `36601525591` and post-merge CI `36601828473` passed.
- Current branch: `feat/report-unavailable-reasons`, based on `main`. This feature has local changes and no PR yet. Live open-PR query returned none before this feature was opened.
- Focused local verification passed: 41 campaign Django tests, Django system check, migration consistency check, Ruff lint/format, and `git diff --check`. Local browser E2E was not run because pytest is absent from this environment. CI is required before merge.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability reference, not first-release scope.
- Local synthetic-data product development is authorized. Staging E2E, backup/restore, rollback, and other release-readiness gates remain before external beta or production.
- PR #135 added the authenticated report shell; #138 established a provider-neutral typed metric contract; #140 connected typed unavailable metrics and identified displayed dates as the planned campaign period; #141 defined provider-neutral metric semantics; #142 mapped official Google Ads API v25 fields for the Search candidate without account access or API requests.
- Current feature adds typed `not_connected`, `unsupported`, `partial`, and `stale` unavailable reasons with reason-specific provenance rules and Turkish per-metric explanations. Only `available` with numeric zero represents a source-confirmed zero. It adds no provider, account connection, persistence, real data, publication, or spend. See ADR-0018.
- The authenticated report remains disconnected and contains no observed values. Google Search mapping leaves reach unavailable; text-ad interactions are not added again to clicks; attributed conversions do not prove delivered leads.
- Keep the Django/PostgreSQL modular monolith and previously approved Heroku staging only. No additional paid service. Real advertiser/customer/lead data, uploads, production AI, platform account connections, publication, advertiser spend, and payments remain out of scope. Never push directly to `main`; successful PRs may be merged after review and required CI under the owner's standing authorization.

## Open risks

- Real-data readiness and release gates remain: secure file handling, privacy/retention, data recipients, provider terms, Türkiye-specific platform/API approvals, token protection/revocation, audit/stop behavior, backup/restore, rollback, and staging browser E2E.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- Google Ads API access/eligibility remains unverified. Source-specific row completeness, zero-row omission, freshness, attribution settings, ingestion, and durable audit are not implemented.

## Next action

Open a PR for the current unavailable-reasons slice, verify required CI and review, and merge only if both pass; then continue source-specific report completeness/freshness rules without building a live adapter.
