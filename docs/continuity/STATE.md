# GrowthTwin — current handoff

Last verified: 2026-09-30 00:16 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `4aa80ea` after PR #161, which added the synthetic sector/channel eligibility contract. Required PR CI `36631135005` and post-merge CI `36631430408` passed.
- Current feature branch: `feat/synthetic-eligibility-preview`, PR [#162](https://github.com/ugurkbcgl-hub/growthtwin/pull/162), based on `4aa80ea`; implementation commit `9e79437`. Required PR CI is pending.
- PR #162 shows the dated source and result for the fixed synthetic home-maintenance campaign in its authenticated local preview. It explains that the result is not legal clearance or publication permission. The 30-day re-review interval exists only to demonstrate fail-closed expiry; it is not an official rule deadline.
- GrowthTwin remains a broad Türkiye advertising product. Local synthetic development is authorized; real advertiser/customer/lead data, live accounts, publication, and payment remain out of scope. Do not exceed existing Heroku staging or add paid services.

## Open risks

- Several sectors and subcategories remain unassessed; qualified Turkish legal review and current platform-policy review remain necessary before live campaigns.
- The eligibility contract accepts caller-supplied claims and does not authenticate sources, persist decisions, or authorize external actions.
- Real-data readiness and release gates remain: privacy/retention, provider terms, platform/API approval, token protection/revocation, audit/stop behavior, backup/restore, rollback, and staging browser E2E.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.

## Next action

Review PR #162 and merge only after required CI passes. Then prioritize the remaining sector matrix gaps before exposing a sector selector; unreviewed categories must stay paused.
