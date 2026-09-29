# GrowthTwin — current handoff

Last verified: 2026-09-29 17:50 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Baseline `main`: `5fb74fb2c07730c163afd4c8ab84e62f202ead59`, PR #127 merged with squash. Required CI `36584727249` and post-merge CI `36585002361` passed.
- Current branch: `feat/synthetic-policy-identifiers`, based on the verified main commit. Synthetic policy version/rule identifiers are being added; changes are not yet in a PR.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Its long-term capability reference does not set first-release scope.
- Local synthetic-data product development is authorized. The remaining Phase 0 staging E2E, backup/restore, and rollback checks are release-readiness gates and do not block local product work.
- PR #122 adds a pure fail-closed campaign action-policy evaluator. PR #126 adds two allowlisted synthetic evidence-source labels and caller-supplied timezone-aware observation time. Its 13 focused tests, local Django system check, Ruff checks, required PR CI, and source review passed. The current branch adds stable informational policy version and evaluated rule IDs; it does not authenticate evidence or persist results.
- The authenticated workspace uses fixed synthetic campaign examples. User uploads, real advertiser/customer/lead data, live account connections, publication, advertiser spend, payments, and production AI are not authorized or implemented.
- Keep the Django/PostgreSQL monolith and approved Heroku staging resources. Add no paid services; never push directly to `main`. Successful PRs may be merged after review and required CI pass under the owner's standing authorization.

## Open risks

- Real-data readiness: secure file handling, privacy/retention, data recipients, provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore, and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- The current evaluator's caller-provided policy evidence is not trusted and is not dispatch authorization. Trusted provenance, any freshness policy, durable audit, atomic budget reservation, and stop/revoke enforcement remain future work.

## Next action

Complete the current `feat/synthetic-policy-identifiers` change with focused tests and documentation. Keep the version and rule IDs in-memory and informational: no evidence authentication, persistence, live integrations, spend reservation, or dispatch authorization.
