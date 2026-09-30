# GrowthTwin — current handoff

Last verified: 2026-09-30 19:36 +0300 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Latest verified `main`: `1ee541e3d832efb3bd5d96ccdc6ea78352125f02` (PR #170). Required CI `36743525443` and post-merge CI `36744652209` passed.
- Current branch: `docs/turkiye-political-ad-eligibility`, based on that `main`. The working tree contains the political/election eligibility research and aligned status-document updates for review.
- PR #171 has not yet been opened. No open PRs were returned by the live GitHub query at the start of this work; the new branch changes are local so far.
- PR #170's Law 4207 update supplements Google's tobacco restriction. PR #171's proposed research records Türkiye's election-period rules, messaging restrictions, Google political-targeting and verification caveats, and remains `needs_review`.

## Completed in this work

- Reviewed current official Google Ads political-content, personalized-ad targeting and election-verification sources, plus KVKK's election-data guide and YSK election decision.
- Updated the existing political/election row and official source list in `docs/product/google-search-turkiye-sector-eligibility.md`. Paid Search interpretation is explicitly unresolved; no campaign is cleared.
- Refreshed `PROJECT.md` and `ROADMAP.md` to remove stale PR #169/#170 pending statuses and reflect verified CI outcomes and the current research slice.
- Documentation-only work; local application tests have not been run. CI for PR #171 is not yet available.

## Open risks

- Election dates and restrictions depend on the current YSK calendar and rules; the cited 2023/1560 decision concerns a past election and must not be reused as a current calendar.
- Exact paid Google Search treatment and advertiser/account verification require current policy checks and qualified legal review. Political campaigns remain paused at `needs_review`.
- The matrix is category-level planning, not legal advice or approval. No sector selector, live account, API, publication, real advertiser data or spend is connected. Staging E2E, backup/restore, rollback and real-data readiness gates remain open.

## Next action

Review the local documentation diff, run `git diff --check`, then commit and open PR #171. Merge only after local review and required CI pass; verify post-merge CI before updating the handoff.
