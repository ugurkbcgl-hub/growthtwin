# GrowthTwin — current handoff

Last verified: 2026-10-15 19:17 +03:00 (Europe/Istanbul).
Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a self-service paid-advertising platform for Türkiye, useful across
industries and advertiser sizes. Continue progressing from the current local
prototype toward a complete campaign journey: brief, creative, plan, launch,
and reporting. Recheck the relevant project decisions and live repository state
before choosing each next implementation step.

## Repository and CI

- At snapshot time, `main` was clean at `23caa58609dfab30275fac993a85d861ecf8bca2`, from PR #276. Recheck the main tip and open PRs before further edits; this handoff refresh itself may create a newer commit.
- PR #276, [R-10 usability observation preparation](https://github.com/ugurkbcgl-hub/growthtwin/pull/276), merged on 2026-10-15. Required CI run `38767091718` and post-merge CI run `38767410913` both passed, including Django tests and browser E2E.
- Local source changes passed `git diff --check`. No test was run locally for the documentation-only change.

## Product progress

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

Run moderated usability observations with at least one first-time advertiser
and one experienced advertiser using the linked script. Record anonymized task
completion, correctness, time, effort, and misunderstandings; compare results
to R-10 acceptance criteria, then prioritize the highest-impact product fix.
Do not call R-10 validated until both participant types have been observed.
