# GrowthTwin — current handoff

Last verified: 2026-09-30 00:00 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `375b058` after PR #159, which added the initial Türkiye advertising, consumer and privacy readiness map. Required CI `36629594340` passed; post-merge CI `36629858494` passed.
- Current feature branch: `research/google-search-eligibility-matrix`, based on `375b058`. This branch contains the dated Google Search Türkiye sector-eligibility matrix and ROADMAP update; PR has not yet been opened.
- The matrix is research/planning only. It distinguishes `eligible`, `restricted`, `not_supported` and `needs_review`; the local-service example is eligible only for synthetic local planning. It does not approve lawfulness, advertiser accounts, GrowthTwin API access or publication.
- Product direction remains broad Türkiye advertisers. Local synthetic development is authorized. Do not use real advertiser/customer/lead data, connect live accounts, publish campaigns, or enable payment. Do not add paid services or exceed the approved Heroku staging setup.

## Open risks

- Multiple sectors and subcategories remain unassessed; stale or missing evidence must fail closed. Qualified Turkish legal review and current platform-policy review remain necessary before live use.
- Real-data readiness and release gates remain: privacy/retention, provider terms, platform/API approval, token protection/revocation, audit/stop behavior, backup/restore, rollback, and staging browser E2E.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.

## Next action

Complete review of the Google Search Türkiye eligibility-matrix PR and merge it only after required CI passes. Then implement a small provider-free eligibility decision contract for local synthetic drafts, following the matrix's fail-closed states; do not connect accounts, call Google, change publication behavior, or introduce real advertiser data.
