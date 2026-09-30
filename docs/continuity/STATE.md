# GrowthTwin — current handoff

Last verified: 2026-09-30 19:41 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Baseline: clean `main` at `dc910a605c44cf7a115ed945dd6ae30c57b56696` (`docs: assess Turkish political ad eligibility (#171)`). PR #171 is merged; no PRs were open at verification.
- PR #171 required CI `36745452282` and post-merge main CI `36745746001` both passed, including browser end-to-end checks.
- This handoff refresh is being prepared on feature branch `docs/low-usage-handoff-20260930`; check its eventual PR and CI live.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. The accepted architecture is a Django 5.2/PostgreSQL modular monolith.
- Local development uses synthetic examples. Do not use real advertiser/customer/lead/patient data, connect live accounts, publish campaigns, incur ad spend, or add paid services without the applicable readiness gate and owner decision. Never expose credentials or secret values.
- The campaign eligibility matrix is category-level planning research, not legal advice or clearance of any offer. Political/election ads remain `needs_review`; exact Google Search treatment, sponsor rules, dates, and legal interpretation require current checks and qualified review. PR #171 only changed documentation/research; it did not add a selector, account/API integration, publishing, or spend.
- Heroku staging has its previously approved resources only. The scheduled session cleanup ran once successfully, but its actual one-off dyno cost is unverified and it is not a real-data retention guarantee.

## Remaining gates

- ROADMAP still lists staging browser E2E, backup/restore, controlled rollback, and final cost/CI recording as incomplete before external beta or production.
- Privacy/data readiness, provider terms, platform approvals, live-action consent and spend enforcement remain open. Do not infer readiness from the local synthetic workflow or policy research.

## Next action

Read-only review the existing staging browser E2E and Phase 0 checklist. Identify the concrete prerequisites and verification steps for staging E2E, backup/restore, rollback, and cost/CI recording using only already-approved resources. Record only verified documentation gaps; do not add paid resources or start a product feature.
