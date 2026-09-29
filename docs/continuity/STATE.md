# GrowthTwin — current handoff

Last verified: 2026-09-29 17:40 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Baseline `main`: `58b57314d45530aa7719b17329dc2aadb38f8e2f`, PR #126 merged with squash. Required CI `36582668937` and post-merge CI `36584339152` passed.
- Current branch: `docs/handoff-pr126-ci`, based on `main`; only verified post-merge status and next-step documentation are changed locally. No open PR was listed at verification.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Its long-term capability reference does not set first-release scope.
- Local synthetic-data product development is authorized. The remaining Phase 0 staging E2E, backup/restore, and rollback checks are release-readiness gates and do not block local product work.
- PR #122 adds a pure fail-closed campaign action-policy evaluator. PR #126 adds two allowlisted synthetic evidence-source labels and caller-supplied timezone-aware observation time. Its 13 focused tests, local Django system check, Ruff checks, required PR CI, and source review passed. These metadata remain unauthenticated, unverified, and non-persistent; there is no freshness threshold, spend reservation, audit record, or live dispatch authorization.
- The authenticated workspace uses fixed synthetic campaign examples. User uploads, real advertiser/customer/lead data, live account connections, publication, advertiser spend, payments, and production AI are not authorized or implemented.
- Keep the Django/PostgreSQL monolith and approved Heroku staging resources. Add no paid services; never push directly to `main`. Successful PRs may be merged after review and required CI pass under the owner's standing authorization.

## Open risks

- Real-data readiness: secure file handling, privacy/retention, data recipients, provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore, and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- The current evaluator's caller-provided policy evidence is not trusted and is not dispatch authorization. Trusted provenance, any freshness policy, durable audit, atomic budget reservation, and stop/revoke enforcement remain future work.

## Next action

Complete the documentation-only handoff update in PR review, then define stable synthetic policy-version and rule identifiers for each deterministic decision, with focused tests. Keep them in-memory and informational: no evidence authentication, persistence, live integrations, spend reservation, or dispatch authorization.
