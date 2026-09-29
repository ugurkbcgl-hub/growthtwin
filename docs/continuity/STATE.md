# GrowthTwin — current handoff

Last verified: 2026-09-30 00:06 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `2514723` after PR #160, which added the dated Google Search Türkiye sector/channel eligibility matrix. Required PR CI `36630378812` and post-merge CI `36630695641` passed.
- Current feature branch: `feat/synthetic-eligibility-contract`, PR [#161](https://github.com/ugurkbcgl-hub/growthtwin/pull/161), based on `2514723`; implementation commit `7f8b0ea`. Required PR CI is pending.
- PR #161 adds a pure in-memory eligibility contract with `eligible`, `restricted`, `not_supported` and `needs_review` outcomes. Missing/stale rule evidence fails closed. It is not connected to a campaign view, database, provider API, or publication and cannot authorize live dispatch.
- GrowthTwin remains a broad Türkiye advertising product. Local synthetic development is authorized; real advertiser/customer/lead data, live accounts, publication, and payment remain out of scope. Do not exceed existing Heroku staging or add paid services.

## Open risks

- Several sectors and subcategories remain unassessed; qualified Turkish legal review and up-to-date platform-policy review remain necessary before live campaigns.
- Real-data readiness and release gates remain: privacy/retention, provider terms, platform/API approval, token protection/revocation, audit/stop behavior, backup/restore, rollback, and staging browser E2E.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.

## Next action

Review PR #161 and merge only after required CI passes. Then connect the synthetic eligibility explanation to the local campaign preview while preserving the existing synthetic-only and no-publication boundaries.
