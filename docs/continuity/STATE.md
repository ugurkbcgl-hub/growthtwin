# GrowthTwin — current handoff

Last verified: 2026-09-29 16:37 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `4ff0cb3233fdddd08be1ba510ad79efc2246374f`; PR #121 is merged. Required CI `36574998136` and post-merge main CI `36575264802` passed. No open PR was listed at the time of verification.
- Current feature branch: `feat/synthetic-action-policy-contracts`. It adds pure fail-closed policy checks for synthetic action review, ten focused tests, ADR-0010, and status corrections in the project/architecture/roadmap/gap-analysis documents. The PR has not yet been opened.
- Local checks: Django system check passed; all ten new policy tests passed; Ruff lint and formatting passed for the approvals package and Django settings.
- The campaign test suite was attempted but PostgreSQL denied creation of its test database. No application secret was exposed. The focused policy suite does not require a database.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability benchmark, not a first-release scope promise.
- Local synthetic-data product development is authorized. Real advertiser/customer/lead data must wait for the readiness gate and separate owner decision. Do not connect live accounts, publish, charge, or spend.
- The authenticated campaign workspace creates a fixed synthetic example. Public registration, user uploads, persistent asset records, AI provider calls, account connections, live forecasts, publication, and payment are not implemented.
- ADR-0008 selects a synthetic city-service quote/contact flow, Google Search as a technical candidate, and the advertiser's own site. ADR-0009 sets future file-safety boundaries. Neither establishes demand, API eligibility, legal readiness, pricing, or permission to publish.
- PRs #120–#121 add and test pure asset workflow contracts only. The current policy evaluator checks caller-supplied evidence and always leaves `live_dispatch_authorized` false; it does not authenticate evidence, reserve spend, or record durable audit.
- Keep the Django/PostgreSQL monolith and approved Heroku staging footprint; add no paid resources. Staging E2E, backup/restore, and rollback remain release-readiness gates; Scheduler one-off cost remains unverified.
- Use feature branches/PRs, never push directly to `main`. Successful PRs may be merged after review and required CI pass under the owner's standing authorization.

## Open risks

- Real-data readiness: secure file handling, privacy/retention, data recipients, provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees and production AI/provider remain undecided or unverified.
- Google forecasts and keyword ideas remain unavailable until eligible authorized sources are connected and verified.
- The synthetic policy contract does not make live dispatch safe. Trusted evidence provenance, concurrent budget reservation, policy versioning, durable audit and stop/revoke enforcement still need design and verification.

## Next action

Finish local review/format validation of `feat/synthetic-action-policy-contracts`, open a PR, and merge only after source review and required CI pass. Keep all external actions disabled.
