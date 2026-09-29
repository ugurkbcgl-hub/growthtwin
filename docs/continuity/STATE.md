# GrowthTwin — current handoff

Last verified: 2026-09-29 10:08 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Snapshot baseline: clean `main` at `c7e87a9` (PR #92), merged with required CI successful. No open PRs were found after the merge.
- PR #92 CI run `36534540580` and post-merge main CI run `36534724665` passed. PR #91 CI run `36533520983` and post-merge run `36533706721` also passed.
- Current branch: `docs/session-draft-handoff-20260929`; this continuity update is pending review.

## Product and safety context

- GrowthTwin targets people and organizations in Türkiye that want to advertise; dental clinics are one possible customer. Omneky is a long-term capability reference, not a first-release scope commitment.
- Local product development with synthetic data is authorized. Keep the accepted Django 5.2/PostgreSQL modular monolith and use feature branches and PRs; never push directly to `main`.
- The current local website path covers a campaign brief, preview, simulated pause, and sample report. Synthetic drafts are session-owned and can be listed, resumed, edited, or deleted. Copy variants are deterministic starting points. There is no AI call, ad-account integration, publication, real campaign spend, or real performance data.
- The existing Heroku staging resources are approved only within the previously agreed budget. Do not add paid services, use real advertiser/customer/patient data, connect live accounts, publish, or deploy production without the required authorization and release gates. Keep trial AI use synthetic.

## Verified work and unresolved gates

- The scheduled Heroku `clearsessions` job's first run at 2026-09-29 00:00 UTC exited successfully. Its actual one-off dyno cost is unverified; Scheduler is best-effort and does not establish a real-data retention guarantee.
- Source review confirmed that the brief/preview labels daily and total sample limits and describes the flow as non-publishing; report figures are labeled synthetic. Visual hierarchy was not verified in the prior review.
- Review found the saved-draft list showed only the brief, daily amount, and duration, so two drafts with the same brief/limits but different brand, audience, or objective were difficult to tell apart. PR #86 now shows those differentiating details, total limit, and creation time. Its focused Django test with two similar synthetic drafts passed; PR CI `36530405593` and post-merge CI `36530563389` also passed.
- Reviewing the edit-save flow confirmed valid creative edits update the same session-owned draft, redirect back to its preview, and show a `role="status"` success message. The preview labels the flow as a draft and explicitly says it does not publish or spend. No specific feedback or accessibility defect was found, so no code change or extra test was needed for this review. The local server is listening at `127.0.0.1:8002`; app security blocked browser automation from refreshing/navigating to the local site, so the rendered visual result was not inspected. The user can refresh the local URL directly in the browser.
- Phase 1 first-visit review found a mobile navigation gap: after submitting a brief, the browser stayed at the page's previous scroll position and could leave the resulting preview below the viewport. PR #89 adds a preview-section URL fragment and scrolls the preview into view when a saved campaign loads. The mobile browser E2E now asserts the target is visible; the first CI run exposed that the fragment alone was insufficient, so explicit scrolling was added. The passing PR and post-merge CI runs include the full Django and browser E2E suites.
- The remaining first-visit checks were reviewed against the current template, form, planning module, and browser E2E: copy is industry-neutral, brand/audience/objective intake is optional, brief/budget/duration are validated, safety labels say no publication/spend and prohibit real data, and mobile keyboard/error feedback plus report navigation are covered. No additional demonstrated gap was found. Visual inspection in the open desktop browser remains unavailable due to the app security block; local server continues listening at `127.0.0.1:8002`.
- A source review of deterministic creative suggestions found they format only supplied brief, brand, and audience text with generic calls to action; existing focused tests cover missing inputs and avoiding invented "best" or "free" claims. The pause/report path labels the action, period, metrics, and results as examples; pause feedback says there is no real campaign. PR #89 CI and post-merge CI passed the existing Django and browser E2E suites. No additional gap requiring a change was found.
- The session-lifetime review found the brief only said the draft is tied to a browser session, and draft deletion had no success feedback. PR #92 now explains that clearing site data or session expiry removes access, confirms successful deletion with an accessible status message, and extends the mobile browser journey to assert deletion. PR #92 and post-merge CI passed. The local server remains available at `127.0.0.1:8002`; visual browser inspection remains blocked by app security.
- Staging browser E2E, backup/restore, rollback, and final cost/CI recording remain gates before an external beta or production. First advertiser workflow/destination, live-action consent and autonomy rules, and production AI/data terms remain undecided.

## Next action

Review what happens to manually edited ad text after the advertiser changes the brief and requests refreshed suggestions; make any overwrite consequences clear and prevent silent loss of saved edits.
