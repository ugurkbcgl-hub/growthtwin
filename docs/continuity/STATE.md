# GrowthTwin — current handoff

Last verified: 2026-09-29 17:12 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Baseline: clean `main` at `6602b95cd6042f6a34a4067f68c54e90f9db7f7d` (`docs: refresh policy implementation status (#123)`). PR #123 is merged; no PRs were open at verification.
- PR #123 required CI `36578045837` and post-merge main CI `36578334751` succeeded.
- This handoff refresh is being prepared on feature branch `docs/low-usage-handoff-20260929-cycle2`; recheck its PR and CI live before acting.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. The long-term capability reference is not a first-release scope promise.
- The accepted architecture is a Django 5.2/PostgreSQL modular monolith. Use feature branches and PRs; never push directly to `main`.
- The authenticated workspace currently uses fixed synthetic campaign examples. Its policy evaluator is a pure, fail-closed contract over caller-supplied, untrusted evidence; it cannot authorize live dispatch. There is no live account connection, publication, payment, advertiser spend, or real advertiser data.
- Keep examples synthetic. Do not add paid services, connect real accounts, publish, spend, or deploy production without the required authorization and release gates. Trial AI endpoints are synthetic evaluation only.
- The existing Heroku staging footprint is within the previously approved budget. The scheduled session cleanup ran once successfully, but its actual one-off dyno cost and any real-data retention guarantee remain unverified.

## Verified work and unresolved gates

- PRs #120–#122 added pure future asset-workflow transitions, tests, and a synthetic campaign action-policy contract. They perform no file/provider operations or live publishing. PRs and post-merge CI passed.
- PR #123 refreshed policy implementation documentation. Its PR and post-merge CI passed.
- Staging browser E2E, backup/restore, rollback, privacy/platform readiness, and final cost recording remain outstanding release gates. First workflow demand, API eligibility, production AI/data terms, pricing, and live-action controls remain undecided or unverified.
- The roadmap's next code candidate is untrusted policy-evidence source/observation-time metadata. This handoff's instruction bars starting product features before Phase 0 completion; defer implementation until that gate is cleared.

## Next action

Do a read-only review of the existing staging browser E2E setup and Phase 0 checklist: identify the concrete prerequisites and verification steps for closing that gate using only already-approved resources. Record any verified gap in the roadmap/handoff; do not add paid resources or start product-feature implementation.
