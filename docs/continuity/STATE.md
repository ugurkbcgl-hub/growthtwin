# GrowthTwin — current handoff

Last verified: 2026-09-29 17:25 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Baseline `main`: `0fc8143d36ec9a60d36aaa8ac0a68b71d018adb3`, PR #125 merged. Its required CI `36581766793` and post-merge CI `36582051706` passed.
- Current branch: `feat/policy-evidence-metadata`, based on the verified main commit above. Changes are local and not yet in a PR. No open PR was listed at verification.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Its long-term capability reference does not set first-release scope.
- Local synthetic-data product development is authorized. The remaining Phase 0 staging E2E, backup/restore, and rollback checks are release-readiness gates and do not block local product work.
- PR #122 adds a pure fail-closed campaign action-policy evaluator. The current feature branch adds two allowlisted synthetic evidence-source labels and caller-supplied timezone-aware observation time. Thirteen focused tests and local Django system check pass. These metadata remain unauthenticated, unverified, and non-persistent; there is no freshness threshold, spend reservation, audit record, or live dispatch authorization.
- The authenticated workspace uses fixed synthetic campaign examples. User uploads, real advertiser/customer/lead data, live account connections, publication, advertiser spend, payments, and production AI are not authorized or implemented.
- Keep the Django/PostgreSQL monolith and approved Heroku staging resources. Add no paid services; never push directly to `main`. Successful PRs may be merged after review and required CI pass under the owner's standing authorization.

## Open risks

- Real-data readiness: secure file handling, privacy/retention, data recipients, provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore, and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- The current evaluator's caller-provided policy evidence is not trusted and is not dispatch authorization. Trusted provenance, any freshness policy, policy versioning, durable audit, atomic budget reservation, and stop/revoke enforcement remain future work.

## Next action

Finish review of the local `feat/policy-evidence-metadata` changes, run the focused style/diff checks, then open a PR. Merge only after source review and required CI pass. The scope is synthetic-only source/time metadata; do not add persistence, live integrations, freshness guarantees, or dispatch authorization.
