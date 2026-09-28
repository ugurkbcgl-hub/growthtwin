# GrowthTwin — current handoff

Last verified: 2026-09-28 22:34 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`. `main` is `a9be467` (PR #54); required PR CI `36472843404` and post-merge CI `36473065414` passed. Both ran Django tests and migration checks. The working tree was clean after merge; there were no open PRs before this handoff update.

## Goal and working rules

- Türkiye is the target market. GrowthTwin serves people and organizations that want to advertise; clinics are one example. Omneky is a long-term breadth benchmark, not a first-release parity promise.
- Validate one advertiser workflow and one publishing destination before broad channel coverage. The first workflow, destination, and review/autonomy defaults remain undecided.
- Advertisers must authorize connected accounts and define enforceable spend, schedule, and content limits before live actions. Pause when information or permission is unclear.
- Keep local, CI, and staging examples synthetic. Do not expose secrets or private advertiser data.
- Approved staging is limited to the existing Heroku Basic dyno, Essential-0 PostgreSQL, and Standard Free Scheduler. Prior Resources estimate was near USD 12/month; actual usage remains unverified. Do not add paid services or enable live publishing/spend without authorization.
- Use feature branches and PRs; never push directly to `main`. The owner authorized merging reviewed PRs when required CI passes.

## Current product state

- Local prototype demonstrates synthetic brief → preview → simulated pause → sample report. Drafts remain session-scoped and synthetic.
- The preview organizes user inputs into a plan summary and indicates missing details. It does not select an advertising channel, connect an account, publish, or show real metrics.
- PR #51 (`15fda3a`) corrected stale README and roadmap status. Required CI `36422821769` and post-merge CI `36423011388` passed.
- PR #52 (`a3e1d22`) added three deterministic, editable copy starting points from the saved brief, brand/product context, and optional audience. Changes save only to the session draft; stale copy is indicated after source changes. No AI, account integration, publishing, or spend. Required CI `36424389194` and post-merge CI `36424605181` passed.
- PR #54 (`a9be467`) improved the information-focused fallback when brand context is absent. It now uses a neutral “Daha fazla bilgi” headline and preserves the brief instead of appending an awkward “hakkında”. Required CI `36472843404` and post-merge CI `36473065414` passed.
- Manual local browser review with synthetic campaign data verified layout, editing, save feedback, regeneration feedback, and saved-value persistence. A local browser POST first returned 500 because migration `site.0005_campaigndraft_creative_variants` had not been applied; the local database was migrated, then the flow succeeded. No tests were run locally; CI ran the Django suite. Local Ruff was unavailable in the checked virtual environment; CI formatting/lint passed.
- Browser review also confirmed that copy with no brand context can still sound like the advertiser's request rather than polished ad copy. The other fallback angles need review before treating them as ad-ready.

## Open decisions and gates

- Select the first advertiser workflow and destination only after validating user need and Türkiye-specific platform eligibility, approval, policy, and reporting.
- Define advertiser consent, spend caps, review/autonomy defaults, and stop conditions before live publishing or spend.
- Session drafts are synthetic. Verify retention/deletion before accepting real advertiser data; staging E2E, backup/restore, and rollback remain external-beta/production gates.
- Heroku Scheduler runs `python manage.py clearsessions` daily at 00:00 UTC. Its first scheduled execution and actual billed one-off dyno usage have not been verified. Per user instruction, defer checking the scheduled run until 2026-10-01 or later. Keep staging data synthetic; this best-effort cadence is not a retention guarantee.
- The prior Heroku Resources estimate was about USD 12/month; actual usage remains unverified. Heroku CLI was unavailable at the last check.
- AI/provider selection and production data-processing terms remain undecided. Recheck provider terms and any tracked research issue before using an external provider.

## Next action

Review and improve the other no-brand/no-audience copy fallbacks so they remain natural and useful while preserving the advertiser's meaning and adding no factual claims. Keep the change local, synthetic, and provider-free; then verify the revised variants in the browser and CI. Do not check the deferred Heroku scheduled run before 2026-10-01.
