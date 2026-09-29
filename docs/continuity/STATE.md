# GrowthTwin — current handoff

Last verified: 2026-09-29 18:48 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Baseline `main`: `a81a1ed7f0fa2ff40bd879725849e9dabd2da4f9`, PR #131 merged with squash. Required CI `36592242914` and post-merge CI `36592558477` passed.
- Current checkout: `main`, clean and up to date with `origin/main`. No open PR was listed at verification.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Its long-term capability reference does not set first-release scope.
- Local synthetic-data product development is authorized. The remaining Phase 0 staging E2E, backup/restore, and rollback checks are release-readiness gates and do not block local product work.
- PR #122 adds a pure fail-closed campaign action-policy evaluator. PR #126 adds two allowlisted synthetic evidence-source labels and caller-supplied timezone-aware observation time. PR #128 adds informational policy version and evaluated-rule identifiers. The 14 focused tests, local Django system check, Ruff checks, PR CI, and post-merge CI passed. These values do not authenticate evidence or persist results.
- The current feature branch adds deterministic creative versions to the authenticated campaign flow, source-fingerprint staleness handling, and owner-only POST regeneration. Twenty-five campaign tests, three browser E2E tests, and 29 related creative/policy/asset tests pass on the repository's SQLite test setting; Django check, migration check, Ruff and diff checks pass. PostgreSQL-backed local test DB creation is blocked because the app role lacks CREATEDB; PR CI will verify the suite on PostgreSQL.
- PR #131 merged that feature; its PostgreSQL PR CI passed. The authenticated sample campaign now displays three provider-free text variants. Selection/editing is not implemented; none of the text is approved or published.
- The authenticated workspace uses fixed synthetic campaign examples. User uploads, real advertiser/customer/lead data, live account connections, publication, advertiser spend, payments, and production AI are not authorized or implemented.
- Keep the Django/PostgreSQL monolith and approved Heroku staging resources. Add no paid services; never push directly to `main`. Successful PRs may be merged after review and required CI pass under the owner's standing authorization.

## Open risks

- Real-data readiness: secure file handling, privacy/retention, data recipients, provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore, and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- The current evaluator's caller-provided policy evidence is not trusted and is not dispatch authorization. Trusted provenance, any freshness policy, durable audit, atomic budget reservation, and stop/revoke enforcement remain future work.

## Next action

Implement owner preference selection among the current synthetic creative variants, tied to their source version and reset on source changes. Keep the selection informational; it must not imply approval, publication, or spend. Do not accept free-text advertiser data or add provider calls.
