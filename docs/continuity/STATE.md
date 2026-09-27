# GrowthTwin — current handoff

Last verified: 2026-09-27 13:30 (Europe/Istanbul)

## Goal and working rules

- Complete Phase 0: establish and demonstrate a repeatable, safe development workflow before implementing product features.
- Product direction: an AI-assisted content, review, publishing, and analytics workflow for dental clinics in Türkiye.
- Keep hosted evaluations synthetic and credentials out of chat and Git. No paid infrastructure, staging deployment, or product features without the relevant Phase 0 gate and explicit user decision.

## Repository and review

- Repository: `https://github.com/ugurkbcgl-hub/growthtwin` (public; `main` is the default branch).
- Pull request [#3](https://github.com/ugurkbcgl-hub/growthtwin/pull/3) was merged on 2026-09-27 as `394d3d4`; the post-merge `Django system check` passed.
- Pull request [#4](https://github.com/ugurkbcgl-hub/growthtwin/pull/4) was merged on 2026-09-27 as `2f53376`; the post-merge CI passed with the Django check, Ruff formatting, and Ruff lint steps.
- Pull request [#5](https://github.com/ugurkbcgl-hub/growthtwin/pull/5) is open on `ci/python-dependency-audit`, adding a pinned Python dependency vulnerability audit. The required CI passed on implementation commit `0337b3e` on 2026-09-27.
- `main` protection now requires a PR and that check from the GitHub Actions app on an up-to-date branch. It also enforces linear history and conversation resolution, applies to administrators, and blocks force-pushes and deletion.
- Use feature branches and PRs. Do not merge an open PR unless the user explicitly asks.

## Phase 0 status

- M2 local Django/PostgreSQL setup is recorded as complete in the roadmap; PostgreSQL service state and the protected secret store were not rechecked in this session.
- M3 is in progress. The Django system-check, Python formatting, and lint checks are active and required; dependency auditing is in PR #5. Type, test, and build checks remain for later, testable work.
- M4 staging and M5 final acceptance remain pending. No product feature implementation has been authorized or started.
- The project record says no paid infrastructure is enabled; this was not rechecked in this session.

## Next action

Recheck the live PR #5 status before merge. Merge only on the user's explicit instruction; after it lands, continue the remaining M3 guardrails. Keep M4 and product work gated.

## Not rechecked this session

- Local Python/PostgreSQL service state and the DPAPI-protected secret store.
- NVIDIA Build account quotas and current model limits.
- Staging provider and recurring-cost estimate for M4.
