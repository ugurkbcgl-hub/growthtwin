# GrowthTwin — current handoff

Last verified: 2026-10-16 22:36 +03:00 (Europe/Istanbul).
Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a self-service paid-advertising platform for Türkiye, useful across
industries and advertiser sizes. Continue progressing from the current local
prototype toward a complete campaign journey: brief, creative, plan, launch,
and reporting. Recheck the relevant project decisions and live repository state
before choosing each next implementation step.

## Repository and CI

- Base `main`: `bbbbdae` (PR #279, merged after review and required CI success
  in run `38774396819`). Post-merge CI `38956058546` is pending at this snapshot.
- Current documentation branch: `docs/rehearsal-handoff-and-google-prerequisites`.
  Recheck live PR/CI and main tip because this snapshot precedes its own commit.
- Local verification: 76 campaign tests (75 passed, 1 PostgreSQL-only skipped),
  plus 5 HTTP and 5 workspace browser tests passed together. Ruff and migration
  consistency checks passed. Tests used isolated in-memory SQLite and fabricated
  accounts. Required CI also passed against PostgreSQL.
- Independent read-only review found no actionable issues.
- Migration 0005 creates rehearsal and event tables only. It was applied to
  disposable test databases; it has not been applied to the existing local or
  Heroku database. A temporary isolated review server was prepared previously,
  but authenticated manual rehearsal review was not completed. Server availability
  has not been rechecked; automated browser coverage passed.

## Product progress

- Owner-scoped synthetic publishing rehearsal now supports start, injected
  failure, retry with the same operation ID, terminal stop and a fresh start.
  Revision + fingerprint checks prevent stale/duplicate actions, and the UI
  shows the last 20 recorded events. Running is only a simulation state.
  ADR-0021 defines the boundary; no external API, worker, real report or spend.
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

Verify the owner's Google Ads test-manager/client and Google Cloud API/OAuth
setup using the [test-account readiness checklist](../product/google-ads-test-account-readiness.md).
Official setup guidance was rechecked on 2026-10-16. No matching Google Ads/OAuth
variables were present in the inspected process; root and apps/web `.env` files
were absent. Other stores/accounts were not inspected, so availability remains
unverified. Do not request secrets in chat. Establish test-only targeting and
credential handling before a first read-only API call or adapter implementation.
R-10 observations remain pending; real advertiser data/publishing/spend remain
behind separate launch gates.
