# GrowthTwin — current handoff

Last verified: 2026-09-27 13:21 (Europe/Istanbul)

## Goal and working rules

- Complete Phase 0: establish and demonstrate a repeatable, safe development workflow before implementing product features.
- Product direction: an AI-assisted content, review, publishing, and analytics workflow for dental clinics in Türkiye.
- Keep hosted evaluations synthetic and credentials out of chat and Git. No paid infrastructure, staging deployment, or product features without the relevant Phase 0 gate and explicit user decision.

## Repository and review

- Repository: `https://github.com/ugurkbcgl-hub/growthtwin` (public; `main` is the default branch).
- Pull request [#3](https://github.com/ugurkbcgl-hub/growthtwin/pull/3) was merged on 2026-09-27 as `394d3d4`; the post-merge `Django system check` passed.
- Pull request [#4](https://github.com/ugurkbcgl-hub/growthtwin/pull/4) is open on `ci/python-quality-checks`, adding pinned Python formatting and lint checks. The required CI passed on implementation commit `c698e46` on 2026-09-27.
- `main` protection now requires a PR and that check from the GitHub Actions app on an up-to-date branch. It also enforces linear history and conversation resolution, applies to administrators, and blocks force-pushes and deletion.
- Use feature branches and PRs. Do not merge an open PR unless the user explicitly asks.

## Phase 0 status

- M2 local Django/PostgreSQL setup is recorded as complete in the roadmap; local services and the protected secret store were not rechecked in this session.
- M3 is in progress. The Django system-check CI is active and required; Python formatting and lint checks are in PR #4. Type, security/dependency, test, and build checks remain for later, testable work.
- M4 staging and M5 final acceptance remain pending. No product feature implementation has been authorized or started.
- The project record says no paid infrastructure is enabled; this was not rechecked in this session.

## Next action

Recheck CI on the current PR #4 revision. Merge only on the user's explicit instruction; after it lands, continue the remaining M3 guardrails. Keep M4 and product work gated.

## Not rechecked this session

- Local Python/PostgreSQL service state and the DPAPI-protected secret store.
- NVIDIA Build account quotas and current model limits.
- Staging provider and recurring-cost estimate for M4.
