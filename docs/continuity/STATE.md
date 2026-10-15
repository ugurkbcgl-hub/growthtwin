# GrowthTwin — current handoff

Last verified: 2026-10-15 19:34 +03:00 (Europe/Istanbul).
Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a self-service paid-advertising platform for Türkiye, useful across
industries and advertiser sizes. Continue progressing from the current local
prototype toward a complete campaign journey: brief, creative, plan, launch,
and reporting. Recheck the relevant project decisions and live repository state
before choosing each next implementation step.

## Repository and CI

- Base `main`: `8b92b44d867aecea7cc3c4659e4eacd4495729e2` (PR #277).
  Post-merge CI `38768174145` completed successfully; the open PR list was empty.
- Current implementation branch: `feat/workspace-campaign-draft-download`.
  The owner-only draft download is prepared for PR review; recheck live PR/CI
  and the main tip because this snapshot is written before its own commit.
- Local verification: 7 download tests and 4 workspace browser tests passed
  together; after adding a changed-preference regression, all 8 download tests
  passed. Ruff and `git diff --check` passed. Tests used isolated in-memory
  SQLite with fabricated accounts, not the existing local database.
- Independent read-only code review found no actionable issues. Required PR
  and post-merge CI for this implementation must be checked live.

## Product progress

- Current owners can download their selected, current creative and plan as a
  plain UTF-8 review file. It contains budget/fee caveats, separate Search
  starter assets and unresolved readiness items. Stale source/version/selection
  links are rejected; other owners receive 404; responses are private/no-store.
  This is not a Google Ads import file or publication approval.
- The authenticated campaign detail prototype has progressive disclosure for
  creative source/character details, campaign suitability evidence, forecast
  search details, and launch-readiness checks. The default view keeps campaign
  goal, media cap, dates, unpublished state, suitability/data caveats, and
  media-fee distinction visible.
- The local synthetic campaign screen was visually reviewed on 2026-10-15.
  The unpublished status and safety context were visible; opening a text detail
  exposed its 27/30 character count and source field. No participant session
  was conducted, and R-10 usability remains unvalidated.
- The moderated beginner and experienced-advertiser task script, scoring form,
  and acceptance criteria are in
  [r10-usability-observation.md](../product/r10-usability-observation.md).
- The site remains a prototype: no production AI provider, connected ad
  account, publication, media spend, or real performance data is active in the
  inspected workflow. Do not present synthetic output as a real ad result.

## Open risks

- Usability results require actual beginner and experienced-advertiser
  participants; source review and automated tests do not establish usability.
- Real-data intake, external AI processing, platform authorization, legal and
  policy review, forecast quality, and production readiness require evidence
  and purpose-specific decisions. Check `PROJECT.md` and `ROADMAP.md` for the
  current gates before enabling those workflows.
- Previous continuity notes could not establish provenance for legacy stored
  drafts. Do not inspect, export, back up, restore, or modify that database
  without a defined, authorized recovery plan.

## Next action

After verifying/finishing the download PR, implement the first explicitly
simulated channel lifecycle in the authenticated workspace: start a rehearsal,
stop it, and safely retry without duplicate actions, using a fake adapter and
owner-scoped records. Read ADR-0008 and the action-policy contracts first.
Keep the unpublished/no-spend status visible and do not invent performance
metrics. R-10 participant observations remain pending acceptance evidence;
they do not block this independent engineering work. Real channel test-account
integration follows only after checking access and the applicable gates.
