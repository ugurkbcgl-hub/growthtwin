# GrowthTwin — current handoff

Last verified: 2026-09-28 12:35 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`. `main` is at `d0b640f` (PR #43); required CI `36404084608` and post-merge CI `36404256264` passed. The documentation handoff PR is being prepared. No deployment, external account connection, or live campaign action occurred.

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
- The preview gives deterministic, non-blocking prompts for missing objective, audience, and brand/offer information. “Review information” returns to the existing form, opens the optional fields when needed, and focuses the first unspecified item. The advertiser can leave all prompts unanswered.
- PR #38 merged as `891584e`; required CI `36398373004` and post-merge CI `36398568486` passed. The workflow included Django tests, system checks, migration consistency, static checks, and the Heroku build checks. Local visual/browser verification was not performed in this step.
- PR #40 merged as `ec53d8b`; required CI `36399557024` and post-merge CI `36399737745` passed. Local visual/browser verification was not performed in this step.
- PR #42 merged as `742f6b4`; the preview label overlap was corrected. The local browser visual review used synthetic session data.
- PR #43 merged as `d0b640f`; required CI `36404084608` and post-merge CI `36404256264` passed. Added an immutable, provider-neutral `CampaignPlan` value object derived from the existing session draft. The object calculates the total limit and optional missing inputs; the server-rendered plan/readiness now uses it. No database migration or new persistence behavior was added.
- No AI call, external account, publishing, real metric, advertiser spend, new paid service, or deployment was added.

## Open decisions and gates

- Select the first advertiser workflow and destination only after validating user need and Türkiye-specific platform eligibility, approval, policy, and reporting.
- Define advertiser consent, spend caps, review/autonomy defaults, and stop conditions before live publishing or spend.
- Session drafts are synthetic. Verify retention and deletion operations before accepting real advertiser data; staging E2E, backup/restore, and rollback remain external-beta/production gates.
- AI/provider selection and production data-processing terms remain undecided. Issue #2 was previously tracking NIM quota research; recheck its current status and provider terms before any NIM use.

## Next action

Define the boundary and acceptance criteria for a persistent `CampaignBrief` domain entity before moving any ORM persistence out of `site`. Keep the prototype synthetic and session-scoped; do not introduce AI, platform selection, account connections, publishing, or spend.
