# GrowthTwin — current handoff

Last verified: 2026-09-29 17:53 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Baseline `main`: `21f47839020cfb91ed4a3d844f6ddef489029ccb`, PR #128 merged with squash. Required CI `36585464840` and post-merge CI `36585760021` passed.
- Current branch: `docs/record-policy-identifiers-merge`, based on the verified main commit; only verified project status and next-step documentation are changed locally.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Its long-term capability reference does not set first-release scope.
- Local synthetic-data product development is authorized. The remaining Phase 0 staging E2E, backup/restore, and rollback checks are release-readiness gates and do not block local product work.
- PR #122 adds a pure fail-closed campaign action-policy evaluator. PR #126 adds two allowlisted synthetic evidence-source labels and caller-supplied timezone-aware observation time. PR #128 adds informational policy version and evaluated-rule identifiers. The 14 focused tests, local Django system check, Ruff checks, PR CI, and post-merge CI passed. These values do not authenticate evidence or persist results.
- The authenticated workspace uses fixed synthetic campaign examples. User uploads, real advertiser/customer/lead data, live account connections, publication, advertiser spend, payments, and production AI are not authorized or implemented.
- Keep the Django/PostgreSQL monolith and approved Heroku staging resources. Add no paid services; never push directly to `main`. Successful PRs may be merged after review and required CI pass under the owner's standing authorization.

## Open risks

- Real-data readiness: secure file handling, privacy/retention, data recipients, provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore, and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- The current evaluator's caller-provided policy evidence is not trusted and is not dispatch authorization. Trusted provenance, any freshness policy, durable audit, atomic budget reservation, and stop/revoke enforcement remain future work.

## Next action

Complete the documentation-only status update, then bring provider-free creative variants into the authenticated workspace campaign path. Keep the work synthetic and owner-scoped, preserve the anonymous demo flow, and add no external AI/provider calls. Ensure creative outputs cannot appear current after relevant campaign inputs change.
