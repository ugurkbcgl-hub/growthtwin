# GrowthTwin — current handoff

Last verified: 2026-09-29 17:18 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Baseline `main`: `7a3d07895b04fb39b97e2177ac17d4ba5098b0ba`, PR #124 merged. Its required CI `36581098202` and post-merge CI `36581436492` passed.
- Current branch: `docs/reconcile-policy-handoff`; it corrects the next-action note in the handoff to match the canonical roadmap and the user's current request. No open PR was listed at verification.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Its long-term capability reference does not set first-release scope.
- Local synthetic-data product development is authorized. The remaining Phase 0 staging E2E, backup/restore, and rollback checks are release-readiness gates and do not block local product work.
- PR #122 adds a pure fail-closed campaign action-policy evaluator and ten tests. It checks caller-supplied evidence and always leaves live dispatch unauthorized. It does not authenticate evidence, prove freshness, reserve spend, or persist an audit record.
- The authenticated workspace uses fixed synthetic campaign examples. User uploads, real advertiser/customer/lead data, live account connections, publication, advertiser spend, payments, and production AI are not authorized or implemented.
- Keep the Django/PostgreSQL monolith and approved Heroku staging resources. Add no paid services; never push directly to `main`. Successful PRs may be merged after review and required CI pass under the owner's standing authorization.

## Open risks

- Real-data readiness: secure file handling, privacy/retention, data recipients, provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore, and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- The current evaluator's caller-provided policy evidence is not trusted and is not dispatch authorization. Source/freshness metadata, policy versioning, durable audit, atomic budget reservation, and stop/revoke enforcement remain future work.

## Next action

Implement the next roadmap item: add synthetic-only policy-evidence source and observation-time metadata with focused tests. Keep it caller-supplied and explicitly untrusted; do not add persistence, live integrations, freshness guarantees, or dispatch authorization.
