# GrowthTwin — current handoff

Last verified: 2026-09-30 19:20 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Latest `main` is `e62f175` after documentation-only PR #169. Its required CI `36742863063` passed. Post-merge CI `36743130604` passed, including Django tests and browser end-to-end tests.
- Current branch: `docs/turkiye-tobacco-eligibility`. It documents Google Ads' tobacco-ad ban alongside Türkiye Law 4207's category-level advertising, promotion and internet-sale restrictions. No specific advertiser or adjacent offer is cleared.
- PR #170 is the tobacco-law documentation update; check its live URL, head commit and required CI before merging. No merge or post-merge CI has been verified for #170.
- This is planning research only. No live account, API, publication, advertiser data, payment, or additional paid service was connected.

## Open risks

- The sector matrix is incomplete. Crypto, political advertising, housing, employment and other regulated categories need exact, dated channel and Turkish-law assessment before a workflow is enabled.
- Category-level research is not legal advice or campaign clearance. Any cessation/public-health campaign and tobacco-adjacent offer needs its own review.
- The eligibility contract remains provider-free and disconnected from accounts, publication, spend and real advertiser data. Staging E2E, backup/restore, rollback and real-data readiness gates remain open.

## Next action

Review PR #170's current diff and required CI; merge only if clean and required CI passes, then verify post-merge CI and continue the Türkiye matrix with political advertising.
