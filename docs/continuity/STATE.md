# GrowthTwin — current handoff

Last verified: 2026-09-30 19:11 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is clean at `cdb0caa` after documentation-only PR #168. Required CI `36741167177` and post-merge CI `36741491268` both passed, including Django tests and browser end-to-end tests.
- Current branch: `docs/update-sept30-research-status`, commit `6710cfd`. PR #169 is open: https://github.com/ugurkbcgl-hub/growthtwin/pull/169. It refreshes only verified status in PROJECT/ROADMAP/STATE after #167 and #168 completed. Required CI is pending.
- PR #167 (ordinary-food research) merged; its required CI `36740203483` and post-merge CI `36740519517` passed.
- PR #168 (adult-services subcategories) merged at `cdb0caa`; required CI `36741167177` and post-merge CI `36741491268` passed.
- Latest matrix additions are source-based category-level research, not legal advice or advertiser/product/service clearance. No live account, API, publication, advertiser data, payment, or additional paid service was connected.
- GitHub Actions produced an `ubuntu-latest` migration annotation for October 19, 2026; it is informational and does not fail CI.

## Open risks

- The sector matrix is incomplete. Tobacco, cryptocurrency, political advertising, housing, employment and other regulated categories require exact, dated platform and Turkish-law checks before any workflow is enabled.
- Adult-service criminal-law application to a specific advertiser, platform or intermediary is fact-specific and needs qualified Turkish legal review before real use. Unassessed categories remain `needs_review`.
- The eligibility contract remains provider-free and disconnected from accounts, publication, spend and real advertiser data. Staging E2E, backup/restore, rollback and real-data readiness release gates remain open.

## Next action

Continue the Türkiye sector matrix with a sourced tobacco advertising eligibility assessment; keep unclear offers at `needs_review` and do not enable live advertising workflows.
