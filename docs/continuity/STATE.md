# GrowthTwin — current handoff

Last verified: 2026-09-29 16:05 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `c3b8ef1bd57bd18331ffc1cb1ca8d7fd683abb67`; PR #118 is merged. Its required CI `36571926602` and post-merge main CI `36572212096` passed. No open PR is known.
- Current branch `docs/secure-asset-intake-contract` is based on main. It adds ADR-0009 and updates the asset-safety implementation order in the roadmap, project brief, ADR index, and this state file. The changes are not yet committed or submitted as a PR.
- PR #117's synthetic daily budget pacing and its PR/main CI passed. Earlier campaign/workspace milestones are in `PROJECT.md` and `ROADMAP.md`.

## Product and safety context

- GrowthTwin is for people and organizations in Türkiye who want to advertise; clinics are one possible sector. Omneky is a long-term capability benchmark, not a first-release scope promise.
- Local synthetic-data product development is authorized. Real advertiser/customer/lead data must wait until the readiness gate and a separate owner decision. Do not connect real accounts, publish, charge, or spend.
- The authenticated campaign workspace creates only a fixed synthetic example. Public registration, user uploads, AI provider calls, account connections, live forecasts, publication, and payment are not implemented.
- ADR-0008 selects a synthetic city-service quote/contact flow, Google Search as a technical candidate, and the advertiser's own site. It does not prove demand, API eligibility, forecast availability, final prices, legal readiness, or publishing permission.
- ADR-0009 sets a contract-first boundary for future user files. It does not authorize upload, durable file storage, parsing, or AI processing. Keep the Django/PostgreSQL monolith and approved Heroku staging footprint; do not add paid resources.
- Staging E2E, backup/restore, and rollback remain release-readiness gates; actual Scheduler one-off cost remains unverified. Use feature branches/PRs; never push directly to main. Successful PRs may be merged after review and required CI pass under the owner's standing authorization.

## Recent verified work

- PRs #113–#115 established the authenticated fixed-sample campaign workspace, bounded owner-scoped synthetic changes, and browser E2E tenant/mobile checks.
- PR #116 improved the Turkish accessible sign-in, return path, and mobile account entry while keeping public registration closed.
- PR #117 added a clearly labeled equal-allocation daily planning average without presenting a platform limit or a performance forecast.
- PR #118 updated project continuity and recorded the next asset safety boundary. PR and post-merge CI passed.

## Open risks

- Real-data readiness: secure file handling, privacy/retention, data recipients, provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees and production AI/provider remain undecided or unverified.
- Google forecasts and keyword ideas remain unavailable until eligible authorized sources are connected and verified.

## Next action

Implement pure, storage/provider-independent asset workflow types and legal state transitions using synthetic examples only. Verify invalid transitions fail closed. Do not accept user files, create durable asset storage, or call AI providers; those require a later reviewed readiness gate and separate owner decision.
