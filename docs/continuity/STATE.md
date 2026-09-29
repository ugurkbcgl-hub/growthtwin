# GrowthTwin — current handoff

Last verified: 2026-09-29 19:23 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Baseline `main`: `102d02068f5bf4e6f6b20d351b0792cdf06a5766`; PR #136 merged with squash. Required CI `36597062416` passed; post-merge CI `36597337620` is running. PR #135 and post-merge CI `36596844250` passed.
- Current checkout: `main`, clean and up to date with `origin/main`. No open PR was listed at verification.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Its long-term capability reference does not set first-release scope.
- Local synthetic-data product development is authorized. The remaining Phase 0 staging E2E, backup/restore, and rollback checks are release-readiness gates and do not block local product work.
- PR #122 adds a pure fail-closed campaign action-policy evaluator. PR #126 adds two allowlisted synthetic evidence-source labels and caller-supplied timezone-aware observation time. PR #128 adds informational policy version and evaluated-rule identifiers. The 14 focused tests, local Django system check, Ruff checks, PR CI, and post-merge CI passed. These values do not authenticate evidence or persist results.
- PR #131 merged deterministic creative versions into the authenticated campaign flow; source-fingerprint staleness handling and owner-only POST regeneration are covered by CI. Main CI and post-merge CI passed.
- PR #133 adds an owner-scoped review preference for one current creative variant, bound to its version and hidden if source inputs change. A new generated version clears the previous preference. Focused validation: 29 campaign tests and three authenticated campaign browser E2E tests pass on SQLite; Django system check, migration check, Ruff lint and formatting pass. PR CI and post-merge CI passed against PostgreSQL.
- ADR-0014 records the review preference boundary. The options remain synthetic and provider-free; preference is not approval, performance data, or publication.
- ADR-0015 defines the authenticated report empty state: no invented metric values, source disconnected, and no ad platform operations. The local implementation now has six unavailable metric categories and explicit source/update status.
- PR #135 adds an owner-scoped campaign report page with six unavailable metric categories and explicit source/update status. It does not create fake metrics or connect a platform. 31 campaign tests and three authenticated campaign browser E2E tests pass on SQLite; browser coverage verifies the six unavailable values and no mobile horizontal overflow. PR PostgreSQL CI passed; post-merge CI is still running.
- The authenticated workspace uses fixed synthetic campaign examples. User uploads, real advertiser/customer/lead data, live account connections, publication, advertiser spend, payments, and production AI are not authorized or implemented.
- Keep the Django/PostgreSQL monolith and approved Heroku staging resources. Add no paid services; never push directly to `main`. Successful PRs may be merged after review and required CI pass under the owner's standing authorization.

## Open risks

- Real-data readiness: secure file handling, privacy/retention, data recipients, provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore, and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- The current evaluator's caller-provided policy evidence is not trusted and is not dispatch authorization. Trusted provenance, any freshness policy, durable audit, atomic budget reservation, and stop/revoke enforcement remain future work.

## Next action

Define and test a provider-neutral report metric contract that distinguishes unavailable from zero and records reporting window, currency where relevant, source, and observation time. Use synthetic examples only; do not connect platforms or fabricate live results.
