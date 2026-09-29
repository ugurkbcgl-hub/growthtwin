# GrowthTwin — current handoff

Last verified: 2026-09-30 00:26 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Base `main` is `115315d` after PR #162. Its required CI run `36632221860` and post-merge CI run `36632509572` passed.
- Current feature branch: `docs/google-ads-sector-gaps`, commit `90804ab`, PR [#163](https://github.com/ugurkbcgl-hub/growthtwin/pull/163), based on `115315d`. Required CI is queued; recheck the live PR before acting.
- PR #163 expands the dated Google Search Türkiye sector matrix with official Google Ads policy research for tobacco, cryptocurrency, political/election advertising, and housing/employment targeting. It also refreshes project, roadmap, and system-gap status. It is research/documentation only; no Turkish legal clearance is implied.
- GrowthTwin remains a broad Türkiye advertising product. Local synthetic development is authorized. Real advertiser/customer/lead data, live accounts, publication, and payment remain out of scope. Do not exceed existing Heroku staging or add paid services.

## Open risks

- Adult services, food/supplements, other sectors and Turkish-law assessment for newly researched categories remain incomplete; keep unreviewed categories paused.
- The eligibility contract accepts caller-supplied claims and does not authenticate sources, persist decisions, or authorize external actions.
- Real-data readiness and release gates remain: privacy/retention, provider terms, platform/API approval, token protection/revocation, audit/stop behavior, backup/restore, rollback, and staging browser E2E.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.

## Next action

Finish PR #163 by checking the latest required CI, reviewing the final diff, merging only if the required check succeeds, and confirming post-merge CI. Then stop this work session; in a later session, continue the remaining sector and Turkish-law research before exposing any sector selector.
