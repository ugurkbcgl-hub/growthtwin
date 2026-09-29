# GrowthTwin — current handoff

Last verified: 2026-09-29 16:24 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `5207ee9ad64bf5480238d5ce9ae0ad99143e1576`; PR #120 is merged. Its required PR CI `36573834624` and post-merge main CI `36574094362` passed.
- Current branch `test/asset-contract-transition-tests` has PR #121 open. It registers the pure asset contract app and adds eight focused tests; docs were updated after PR #120. Local targeted tests and Ruff checks passed. Verify CI on the latest PR commit before merge.

## Product and safety context

- GrowthTwin is for people and organizations in Türkiye who want to advertise; clinics are one possible sector. Omneky is a long-term capability benchmark, not a first-release scope promise.
- Local synthetic-data product development is authorized. Real advertiser/customer/lead data must wait until the readiness gate and a separate owner decision. Do not connect real accounts, publish, charge, or spend.
- The authenticated campaign workspace creates only a fixed synthetic example. Public registration, user uploads, persistent asset records, AI provider calls, account connections, live forecasts, publication, and payment are not implemented.
- ADR-0008 selects a synthetic city-service quote/contact flow, Google Search as a technical candidate, and the advertiser's own site. ADR-0009 sets future file-safety boundaries, but neither establishes demand, API eligibility, legal readiness, price, or permission to publish.
- PR #120 adds immutable, non-persistent asset state and permission values. PR #121 tests declaration requirements, clean/unsafe/error scan outcomes, extraction, provider permission separation, invalid construction, and deletion. Passing contract tests do not establish file-handling readiness.
- Keep the Django/PostgreSQL monolith and approved Heroku staging footprint; do not add paid resources. Staging E2E, backup/restore, and rollback remain release-readiness gates; actual Scheduler one-off cost remains unverified.
- Use feature branches/PRs, never push directly to main. Successful PRs may be merged after review and required CI pass under the owner's standing authorization.

## Open risks

- Real-data readiness: secure file handling, privacy/retention, data recipients, provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees and production AI/provider remain undecided or unverified.
- Google forecasts and keyword ideas remain unavailable until eligible authorized sources are connected and verified.

## Next action

Review PR #121, check its latest required CI, and merge only if the change is clean and CI passes. Keep uploads, persistence, parsing, provider calls, and real data closed. Then choose the next readiness item from the product gap analysis.
