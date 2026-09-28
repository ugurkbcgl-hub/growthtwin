# GrowthTwin — current handoff

Last verified: 2026-09-28 15:53 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`. `main` is `a3e1d22` (PR #52); required PR CI `36424389194` and post-merge CI `36424605181` passed, including Django tests and migration checks. The working tree was clean after merge; there were no open PRs at the last check.

## Goal and working rules

- Türkiye is the target market. GrowthTwin serves people and organizations that want to advertise; clinics are one example. Omneky is a long-term breadth benchmark, not a first-release parity promise.
- Validate one advertiser workflow and one publishing destination before broad channel coverage. The first workflow, destination, and review/autonomy defaults remain undecided.
- Advertisers must authorize connected accounts and define enforceable spend, schedule, and content limits before live actions. Pause when information or permission is unclear.
- Keep local, CI, and staging examples synthetic. Do not expose secrets or private advertiser data.
- Approved staging is limited to the existing Heroku Basic dyno, Essential-0 PostgreSQL, and Standard Free Scheduler. Prior Resources estimate was near USD 12/month; actual usage remains unverified. Do not add paid services or enable live publishing/spend without authorization.
- Use feature branches and PRs; never push directly to `main`. The owner authorized merging reviewed PRs when required CI passes.

## Current product state

- Local prototype demonstrates synthetic brief → preview → simulated pause → sample report. Drafts remain session-scoped and synthetic.
- The preview organizes user inputs into a plan summary and indicates missing details. It does not select an advertising channel, create a connected account, publish, or show real metrics.
- PR #51 (`15fda3a`) corrected the README and roadmap to reflect the actual product prototype. Required CI `36422821769` and post-merge CI `36423011388` passed.
- PR #52 (`a3e1d22`) added three deterministic, editable copy starting points from the saved brief, brand/product context, and optional audience. Changes save only to the session draft; stale copy is indicated after source changes. No AI provider, account integration, publishing, or spend is involved. Required CI `36424389194` and post-merge CI `36424605181` passed, including Django tests, migration checks, formatting/lint, and build checks.
- A manual browser visual review of the new copy editor has not been performed. Local tests were not separately run; CI ran the Django test suite.

## Open decisions and gates

- Select the first advertiser workflow and destination only after validating user need and Türkiye-specific platform eligibility, approval, policy, and reporting.
- Define advertiser consent, spend caps, review/autonomy defaults, and stop conditions before live publishing or spend.
- Session drafts are synthetic. Verify retention and deletion operations before accepting real advertiser data; staging E2E, backup/restore, and rollback remain external-beta/production gates.
- The Heroku Scheduler runs `python manage.py clearsessions` daily at 00:00 UTC. Its first scheduled execution and actual billed one-off dyno usage have not been verified. Per user's instruction, defer checking this scheduled run until 2026-10-01 or later. Keep staging data synthetic; this best-effort cadence is not a retention guarantee.
- The prior Heroku Resources estimate was about USD 12/month; actual usage has not been verified. Heroku CLI was unavailable at the last check.
- AI/provider selection and production data-processing terms remain undecided. Recheck provider terms and any tracked research issue before using an external provider.

## Next action

Manually review the editable creative-copy flow in the local browser using synthetic campaign data. Fix any usability or display issues found; then select the next narrow local product slice. Do not check the deferred Heroku scheduled run before 2026-10-01.
