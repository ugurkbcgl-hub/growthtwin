# GrowthTwin — current handoff

Last verified: 2026-09-29 16:13 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `1f6ad5b7b049aa025c3e570ab9f563b8814d8b92`; PR #119 is merged. Its required CI `36572692042` and post-merge main CI `36572958105` passed.
- Current branch `feat/asset-workflow-contracts` is based on main at commit `92b6fb43e1be2e0c0ea21fe8a45b114e154c9efc`. PR #120 is open; required CI `36573448094` is in progress. It introduces storage/provider-independent asset workflow types and fail-closed transitions; no file operations, persistence, or network calls.
- PR #117 budget-pacing behavior and PR #118 continuity updates are merged; their required and post-merge CI runs passed.

## Product and safety context

- GrowthTwin is for people and organizations in Türkiye who want to advertise; clinics are one possible sector. Omneky is a long-term capability benchmark, not a first-release scope promise.
- Local synthetic-data product development is authorized. Real advertiser/customer/lead data must wait until the readiness gate and a separate owner decision. Do not connect real accounts, publish, charge, or spend.
- The authenticated campaign workspace creates only a fixed synthetic example. Public registration, user uploads, AI provider calls, account connections, live forecasts, publication, and payment are not implemented.
- ADR-0008 selects a synthetic city-service quote/contact flow, Google Search as a technical candidate, and the advertiser's own site. It does not prove demand, API eligibility, forecast availability, final prices, legal readiness, or publishing permission.
- ADR-0009 defines a contract-first boundary for future user files. It does not authorize upload, durable file storage, parsing, or AI processing. Keep the Django/PostgreSQL monolith and approved Heroku staging footprint; do not add paid resources.
- Staging E2E, backup/restore, and rollback remain release-readiness gates; actual Scheduler one-off cost remains unverified. Use feature branches/PRs; never push directly to main. Successful PRs may be merged after review and required CI pass under the owner's standing authorization.

## Recent verified work

- PRs #113–#115 established the authenticated fixed-sample campaign workspace, bounded owner-scoped synthetic changes, and browser E2E tenant/mobile checks.
- PR #116 improved Turkish accessible sign-in, the return path, and mobile account entry while keeping public registration closed.
- PR #117 added a clearly labeled equal-allocation daily planning average without presenting a platform limit or performance forecast.
- PR #118 refreshed project continuity. PR #119 added ADR-0009 for safe asset intake; PR and post-merge main CI passed.
- PR #120 packages the pure asset state contract. Local tests were not run; required GitHub CI is in progress.

## Open risks

- Real-data readiness: secure file handling, privacy/retention, data recipients, provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees and production AI/provider remain undecided or unverified.
- Google forecasts and keyword ideas remain unavailable until eligible authorized sources are connected and verified.

## Next action

Review the pure asset workflow contract and confirm PR #120's required CI. Merge only if review is clean and CI passes. Do not add upload, persistence, parsing, or AI-provider behavior. After that contract is reviewed, define synthetic-only transition tests before considering isolated local file handling.
