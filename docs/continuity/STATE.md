# GrowthTwin — current handoff

Last verified: 2026-09-29 16:22 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `5207ee9ad64bf5480238d5ce9ae0ad99143e1576`; PR #120 is merged. Required PR CI `36573834624` and post-merge main CI `36574094362` passed.
- Current branch `test/asset-contract-transition-tests` is based on main. It registers the pure asset contract app for test discovery and adds eight focused tests. Project/roadmap/gap/continuity docs reflect this work. Changes are uncommitted and no PR is open.
- Local targeted run `manage.py test growthtwin.modules.assets.tests --settings=config.test_settings` passed: 8 tests, Django system check clean. Targeted Ruff format and lint checks passed in the project virtual environment.

## Product and safety context

- GrowthTwin is for people and organizations in Türkiye who want to advertise; clinics are one possible sector. Omneky is a long-term capability benchmark, not a first-release scope promise.
- Local synthetic-data product development is authorized. Real advertiser/customer/lead data must wait until the readiness gate and a separate owner decision. Do not connect real accounts, publish, charge, or spend.
- The authenticated campaign workspace creates only a fixed synthetic example. Public registration, user uploads, persistent asset records, AI provider calls, account connections, live forecasts, publication, and payment are not implemented.
- ADR-0008 selects a synthetic city-service quote/contact flow, Google Search as a technical candidate, and the advertiser's own site. ADR-0009 sets future file-safety boundaries, but neither establishes demand, API eligibility, legal readiness, price, or permission to publish.
- PR #120 adds immutable, non-persistent asset state and permission values. This branch tests declaration requirements, clean/unsafe/error scan outcomes, extraction, separate provider permission, invalid construction, and deletion. Tests do not imply that file handling is ready.
- Keep the Django/PostgreSQL monolith and approved Heroku staging footprint; do not add paid resources. Staging E2E, backup/restore, and rollback remain release-readiness gates; actual Scheduler one-off cost remains unverified.
- Use feature branches/PRs, never push directly to main. Successful PRs may be merged after review and required CI pass under the owner's standing authorization.

## Open risks

- Real-data readiness: secure file handling, privacy/retention, data recipients, provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees and production AI/provider remain undecided or unverified.
- Google forecasts and keyword ideas remain unavailable until eligible authorized sources are connected and verified.

## Next action

Review the eight asset contract tests and CI, open a PR, and merge only if clean and required CI passes. Keep uploads, persistence, parsing, provider calls, and real data closed. After that, choose the next readiness task from the product gap analysis; do not infer that contract tests make file handling ready.
