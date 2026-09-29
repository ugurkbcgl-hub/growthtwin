# GrowthTwin — current handoff

Last verified: 2026-09-29 16:49 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `751e6dd0c5aeff6c69e3590980a9b7d844f9dbfa`; PR #122 is merged. Required PR CI `36576865860` and post-merge main CI `36577137802` passed. No open PR was listed after the merge.
- Current branch `docs/post-policy-current-state`, PR [#123](https://github.com/ugurkbcgl-hub/growthtwin/pull/123) open. It updates the project, architecture, roadmap, gap analysis, and handoff snapshot for PR #122. Required CI run `36577941774` was in progress at verification.
- PR #122 adds a pure synthetic action-policy evaluator and ten focused tests. Local Django system check, policy tests, Ruff lint/format, and post-merge full Django and browser E2E CI passed. Local campaign integration tests could not create their PostgreSQL test database because the local role lacks that privilege.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability benchmark, not a first-release scope promise.
- Local synthetic-data product development is authorized. Real advertiser/customer/lead data must wait for the readiness gate and separate owner decision. Do not connect live accounts, publish, charge, or spend.
- The authenticated campaign workspace creates a fixed synthetic example. Public registration, user uploads, persistent asset records, AI provider calls, account connections, live forecasts, publication, and payment are not implemented.
- ADR-0008 selects a synthetic city-service quote/contact flow, Google Search as a technical candidate, and the advertiser's own site. ADR-0009 sets future file-safety boundaries. Neither establishes demand, API eligibility, legal readiness, pricing, or permission to publish.
- PR #122 checks caller-supplied evidence and always leaves live dispatch unauthorized. It does not authenticate evidence, reserve spend, prove freshness, or persist an audit record.
- Keep the Django/PostgreSQL monolith and approved Heroku staging footprint; add no paid resources. Staging E2E, backup/restore, and rollback remain release-readiness gates; Scheduler one-off cost remains unverified.
- Use feature branches/PRs, never push directly to `main`. Successful PRs may be merged after review and required CI pass under the owner's standing authorization.

## Open risks

- Real-data readiness: secure file handling, privacy/retention, data recipients, provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees and production AI/provider remain undecided or unverified.
- Google forecasts and keyword ideas remain unavailable until eligible authorized sources are connected and verified.
- Before live policy use, design trusted evidence provenance, policy versioning, durable audit, concurrent budget reservation, and stop/revoke enforcement. The current evaluator is only a local synthetic contract.

## Next action

Check CI for PR #123 after its latest commit and merge after review and required CI pass. Then add a small synthetic-only metadata contract for policy evidence source and observation time; keep it explicitly untrusted and disconnected from live dispatch.
