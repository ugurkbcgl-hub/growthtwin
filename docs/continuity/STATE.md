# GrowthTwin — current handoff

Last verified: 2026-09-29 00:06 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`. `main` is `52e93e3` (PR #60). Required PR CI `36483491236` and post-merge CI `36483681415` passed. The working tree was clean and there were no open PRs before this handoff update.

## Goal and working rules

- Türkiye is the target market. GrowthTwin serves people and organizations that want to advertise; clinics are one example. Omneky is a long-term breadth benchmark, not a first-release parity promise.
- Local synthetic-data product development is authorized. Keep using the existing Django/PostgreSQL app and CI; use branches and PRs, never push directly to `main`.
- Advertisers must authorize connected accounts and define enforceable spend, schedule, and content limits before live actions. Pause when information or permission is unclear.
- Keep local, CI, and staging examples synthetic. Do not expose secrets or private advertiser data.
- Do not add paid services or enable live publishing/spend without authorization. Heroku Scheduler run review was deferred until 2026-10-01 or later; do not inspect it earlier.

## Current product state

- Local prototype demonstrates synthetic brief → preview → simulated pause → sample report. Drafts remain session-scoped and synthetic.
- PR #51 (`15fda3a`) corrected stale README and roadmap status. Required CI `36422821769` and post-merge CI `36423011388` passed.
- PR #52 (`a3e1d22`) added three deterministic, editable copy starting points from the saved brief, brand/product context, and optional audience. No AI, account integration, publishing, or spend. Required CI `36424389194` and post-merge CI `36424605181` passed.
- PR #54 (`a9be467`) improved the information-focused fallback when brand context is absent. Required CI `36472843404` and post-merge CI `36473065414` passed.
- Manual local browser review with synthetic campaign data verified layout, editing, save feedback, regeneration feedback, and saved-value persistence. A missing local migration was applied during that review; local Ruff was unavailable, while CI formatting/lint passed.
- PR #56 (`f799426`) stopped the audience-focused variant from appending “Detayları incele” to the brief when no audience is given; the CTA remains separate. Three focused local tests passed, and the browser confirmed the no-brand/no-audience brief stays unchanged in the audience- and information-focused bodies. Required CI `36474994196` and post-merge CI `36475232546` passed.
- PR #58 (`a978014`) clarified that these are synthetic, editable starting points; when brand or audience context is missing, the brief may be shown unchanged and should be edited and checked before publication. The note is more readable. Four focused local tests and browser review passed. A database-backed local test was unavailable because the local PostgreSQL role cannot create test databases; the focused UI test uses no database, and CI ran the full Django suite. Required CI `36478847264` and post-merge CI `36479049872` passed.
- Comparing five synthetic inputs found that the audience- and information-focused variants could omit the offer when both brand and audience were supplied. PR #60 (`52e93e3`) keeps the brief content in those bodies, includes a shortened audience in the audience-focused body, and keeps the brand in the headline. Five focused local tests and the full CI suite passed; required CI `36483491236` and post-merge CI `36483681415` passed.
- Copy remains deterministic and provider-free. It is an editable starting point, not an AI-generated or publish-ready ad.

## Open decisions and gates

- Select the first advertiser workflow and publishing destination only after validating user need and Türkiye-specific platform eligibility, approval, policy, and reporting.
- Define advertiser consent, spend caps, review/autonomy defaults, and stop conditions before live publishing or spend.
- Session drafts are synthetic. Verify retention/deletion before accepting real advertiser data; staging E2E, backup/restore, and rollback remain external-beta/production gates.
- Heroku Scheduler's first scheduled execution and actual billed one-off dyno usage remain unverified. Keep staging data synthetic; the best-effort cleanup cadence is not a retention guarantee. Do not inspect the scheduled run before 2026-10-01.
- AI/provider selection and production data-processing terms remain undecided. Recheck provider terms before using an external provider.

## Next action

Review length edge cases with longer synthetic briefs, brands, and audiences. Confirm the 240-character copy fields retain the essential offer and audience rather than truncating one away; adjust only if focused examples reveal information loss. Keep all text provider-free, add focused tests, and review the rendered result. Do not use real advertiser data or check Heroku Scheduler before 2026-10-01.
