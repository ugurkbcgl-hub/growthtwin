# GrowthTwin — current handoff

Last verified: 2026-09-29 09:09 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Snapshot baseline: clean `main` at `334e2dccdaff78f8fb88693138a9b6e377ca546f` (`docs: record preview clarity review (#84)`). PR #84 is merged; no PRs were open at verification.
- Main CI run `36529419983` completed successfully. PR #84's required check and its post-merge main run also succeeded.
- This handoff refresh is being prepared on feature branch `docs/usage-handoff-20260929`; verify its eventual PR and CI status live before acting.

## Product and safety context

- GrowthTwin targets people and organizations in Türkiye that want to advertise; dental clinics are one possible customer. Omneky is a long-term capability reference, not a first-release scope commitment.
- Local product development with synthetic data is authorized. Keep the accepted Django 5.2/PostgreSQL modular monolith and use feature branches and PRs; never push directly to `main`.
- The current local website path covers a campaign brief, preview, simulated pause, and sample report. Synthetic drafts are session-owned and can be listed, resumed, edited, or deleted. Copy variants are deterministic starting points. There is no AI call, ad-account integration, publication, real campaign spend, or real performance data.
- The existing Heroku staging resources are approved only within the previously agreed budget. Do not add paid services, use real advertiser/customer/patient data, connect live accounts, publish, or deploy production without the required authorization and release gates. Keep trial AI use synthetic.

## Verified work and unresolved gates

- The scheduled Heroku `clearsessions` job's first run at 2026-09-29 00:00 UTC exited successfully. Its actual one-off dyno cost is unverified; Scheduler is best-effort and does not establish a real-data retention guarantee.
- Source review confirmed that the brief/preview labels daily and total sample limits and describes the flow as non-publishing; report figures are labeled synthetic. Visual hierarchy was not verified in the prior review.
- Staging browser E2E, backup/restore, rollback, and final cost/CI recording remain gates before an external beta or production. First advertiser workflow/destination, live-action consent and autonomy rules, and production AI/data terms remain undecided.

## Next action

Review the saved-draft list and resume/edit flow against the self-service goal: verify that users can identify the synthetic draft being edited and understand that edits remain drafts without publication or spend. Fix only demonstrated comprehension, ownership, or accessibility gaps; use focused local synthetic-data review and checks.
