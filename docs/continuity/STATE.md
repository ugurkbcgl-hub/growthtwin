# GrowthTwin — current handoff

Last verified: 2026-09-27 12:52 (Europe/Istanbul)

## Goal and working rules

- Complete Phase 0: establish and demonstrate a repeatable, safe development workflow before implementing product features.
- Product direction: an AI-assisted content, review, publishing, and analytics workflow for dental clinics in Türkiye.
- Keep hosted evaluations synthetic and credentials out of chat and Git. No paid infrastructure, staging deployment, or product features without the relevant Phase 0 gate and explicit user decision.

## Repository and review

- Repository: `https://github.com/ugurkbcgl-hub/growthtwin` (public; `main` is the default branch).
- Working branch: `docs/qwen3-local-evaluation`; pull request [#3](https://github.com/ugurkbcgl-hub/growthtwin/pull/3) was open against `main` at the last check.
- GitHub Actions `Django system check` passed on the previously verified PR head `99aa57f` on 2026-09-27. The PR review findings have been addressed in the current branch; the required check for the updated revision is pending verification.
- `main` protection now requires a PR and that check from the GitHub Actions app on an up-to-date branch. It also enforces linear history and conversation resolution, applies to administrators, and blocks force-pushes and deletion.
- Use feature branches and PRs. Do not merge PR #3 unless the user asks.

## Phase 0 status

- M2 local Django/PostgreSQL setup is recorded as complete in the roadmap; local services and the protected secret store were not rechecked in this session.
- M3 is in progress. The minimal Django system-check CI is active and required; wider lint, security, and product-path checks remain for later, testable work.
- M4 staging and M5 final acceptance remain pending. No product feature implementation has been authorized or started.
- The project record says no paid infrastructure is enabled; this was not rechecked in this session.

## Next action

Verify the required check on the updated PR #3 revision and review its result. After the PR is merged through the approved flow, continue the remaining M3 guardrails. Keep M4 and product work gated; do not merge autonomously.

## Not rechecked this session

- Local Python/PostgreSQL service state and the DPAPI-protected secret store.
- NVIDIA Build account quotas and current model limits.
- Staging provider and recurring-cost estimate for M4.
