# GrowthTwin — current handoff

Last verified: 2026-09-29 10:42 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Clean `main` at `f524a11` (PR #98); no open PRs at this snapshot.
- PR #98 CI run `36537946501` passed. Its post-merge `main` run `36538134330` was still in progress at this snapshot.
- PR #97 CI run `36537625405` and post-merge run `36537842405` passed.
- PR #96 CI run `36536971429` and post-merge run `36537179131` passed.

## Product and safety context

- GrowthTwin targets people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability reference, not first-release scope.
- Local product development with synthetic data is authorized. Keep Django 5.2/PostgreSQL modular monolith; use feature branches and PRs; do not push directly to `main`.
- The local site demonstrates brief → campaign preview → editable deterministic copy → simulated pause → sample report. Drafts belong to an anonymous session and are stored in PostgreSQL. No AI provider, ad account, publication, real spend, or real performance metrics are connected.
- The first-visit notice now accurately says brief data is sent to the GrowthTwin app and temporarily stored as a session draft; this prototype does not send it to AI services or ad platforms, publish ads, or spend money. Real or sensitive information must not be used.
- Existing Heroku staging is approved only within the previously agreed budget and synthetic-data boundary. The daily `clearsessions` job's first run succeeded on 2026-09-29; actual one-off dyno cost is unverified, and Scheduler is best-effort. Staging E2E, backup/restore, rollback, and final cost/CI recording remain gates before external beta or production.
- First advertiser workflow/destination, live-action consent/autonomy rules, and production AI/data terms remain undecided. Do not connect real accounts, publish, spend, deploy production, or add paid services without required authorization.

## Recent verified work

- PR #89 fixed the mobile post-submit preview scroll; PR and post-merge CI passed.
- PR #92 clarified session-draft access expiry and added accessible delete confirmation; PR and post-merge CI passed.
- PR #94 warns that regeneration replaces all edited copy; the focused mobile E2E and post-merge CI passed.
- The campaign-plan/copy review compared two distinct synthetic advertiser briefs. Summaries reflect user-entered objective, audience, offer, and budget; deterministic copy formats supplied facts with no additional factual claims. No defect was demonstrated.
- Review of editing an existing draft confirmed the brief and plan update together; creative copy stays visibly marked stale until the advertiser deliberately regenerates it, preserving edits. Existing mobile E2E covers this path; no inconsistency was found.
- The first-visit content review found the inaccurate “nothing is sent anywhere” notice. PR #96 corrected the data-flow statement and added a focused regression test; PR and post-merge CI passed.
- Visual inspection through the open browser was unavailable because app security blocked browser automation. The local server at `127.0.0.1:8002` was reported running earlier; current availability was not rechecked.

## Next action

Compare the Phase 1 acceptance criteria with the implemented campaign journey and focused browser E2E to identify any remaining demonstrable gap before considering Phase 2; keep product examples synthetic and do not add publishing or external services.
