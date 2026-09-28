# GrowthTwin — current handoff

Last verified: 2026-09-28 11:40 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`. `main` is at `891584efa71f9e2aeb64d79ab53959fba2637a19`; PR #38 required CI `36398373004` and post-merge CI `36398568486` passed. Working tree was clean and no open PRs were listed. No deployment, external account connection, or live campaign action occurred.

## Goal and working rules

- Türkiye is the target market. GrowthTwin serves people and organizations that want to advertise; clinics are one example. Omneky is a long-term breadth benchmark, not a first-release parity promise.
- Validate one advertiser workflow and one publishing destination before broad channel coverage. The first workflow, destination, and review/autonomy defaults remain undecided.
- Advertisers must authorize connected accounts and define enforceable spend, schedule, and content limits before live actions. Pause when information or permission is unclear.
- Keep local, CI, and staging examples synthetic. Do not expose secrets or private advertiser data.
- Only previously approved paid infrastructure is the existing Heroku Basic dyno plus Essential-0 PostgreSQL, about USD 12/month before tax. Do not add paid services or enable live publishing/spend without authorization.
- Use feature branches and PRs; never push directly to `main`. The owner has authorized merging reviewed PRs when required CI passes.

## Current product state

- The public local prototype demonstrates synthetic brief → preview → simulated pause → sample report.
- Session-scoped drafts can be created, listed, resumed, edited, and discarded. They store brief, optional brand/product context, optional generic campaign objective, optional audience, daily spend boundary, and duration.
- The preview now organizes those inputs into a campaign-plan summary and calculates the total limit. Missing objective, audience, and brand context are marked as unspecified. It explicitly says no channel or creative format has been selected and no ad is generated or published.
- PR #38 merged as `891584e`; required CI `36398373004` and post-merge CI `36398568486` passed. The workflow included Django tests, system checks, migration consistency, static checks, and the Heroku build checks. Local visual/browser verification was not performed in this step.
- No AI call, external account, publishing, real metric, advertiser spend, new paid service, or deployment was added.

## Open decisions and gates

- Select the first advertiser workflow and destination only after validating user need and Türkiye-specific platform eligibility, approval, policy, and reporting.
- Define advertiser consent, spend caps, review/autonomy defaults, and stop conditions before live publishing or spend.
- Session drafts are synthetic. Verify retention and deletion operations before accepting real advertiser data; staging E2E, backup/restore, and rollback remain external-beta/production gates.
- AI/provider selection and production data-processing terms remain undecided. Issue #2 was previously tracking NIM quota research; recheck its current status and provider terms before any NIM use.

## Next action

Add a deterministic, non-blocking plan-readiness explanation that identifies which high-impact campaign inputs are still unspecified and lets the advertiser improve them without inventing a destination or creative. Keep this local and synthetic; do not add AI, account connection, publishing, or spend.
