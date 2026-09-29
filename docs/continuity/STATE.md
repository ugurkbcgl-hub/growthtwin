# GrowthTwin — current handoff

Last verified: 2026-09-29 09:23 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Snapshot baseline: clean `main` at `6f4c602` (PR #86), merged with required CI successful. No open PRs were found after the merge.
- PR #86 (`74a659d`) and post-merge main CI run `36530563389` passed.
- Current branch: `docs/saved-draft-review-handoff`; this continuity update is pending review.

## Product and safety context

- GrowthTwin targets people and organizations in Türkiye that want to advertise; dental clinics are one possible customer. Omneky is a long-term capability reference, not a first-release scope commitment.
- Local product development with synthetic data is authorized. Keep the accepted Django 5.2/PostgreSQL modular monolith and use feature branches and PRs; never push directly to `main`.
- The current local website path covers a campaign brief, preview, simulated pause, and sample report. Synthetic drafts are session-owned and can be listed, resumed, edited, or deleted. Copy variants are deterministic starting points. There is no AI call, ad-account integration, publication, real campaign spend, or real performance data.
- The existing Heroku staging resources are approved only within the previously agreed budget. Do not add paid services, use real advertiser/customer/patient data, connect live accounts, publish, or deploy production without the required authorization and release gates. Keep trial AI use synthetic.

## Verified work and unresolved gates

- The scheduled Heroku `clearsessions` job's first run at 2026-09-29 00:00 UTC exited successfully. Its actual one-off dyno cost is unverified; Scheduler is best-effort and does not establish a real-data retention guarantee.
- Source review confirmed that the brief/preview labels daily and total sample limits and describes the flow as non-publishing; report figures are labeled synthetic. Visual hierarchy was not verified in the prior review.
- Review found the saved-draft list showed only the brief, daily amount, and duration, so two drafts with the same brief/limits but different brand, audience, or objective were difficult to tell apart. PR #86 now shows those differentiating details, total limit, and creation time. Its focused Django test with two similar synthetic drafts passed; PR CI `36530405593` and post-merge CI `36530563389` also passed. The local server is listening at `127.0.0.1:8002`; app security blocked browser automation from refreshing/navigating to the local site, so the rendered visual result was not inspected. The user can refresh the local URL directly in the browser.
- Staging browser E2E, backup/restore, rollback, and final cost/CI recording remain gates before an external beta or production. First advertiser workflow/destination, live-action consent and autonomy rules, and production AI/data terms remain undecided.

## Next action

Review how saving edits to an existing draft returns to its preview and communicates that the updated version was saved; confirm it remains an unpublished, no-spend draft. Fix only demonstrated feedback or accessibility gaps using synthetic content.
