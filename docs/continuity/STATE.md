# GrowthTwin — current handoff

Last verified: 2026-09-29 19:58 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Baseline `main`: `9f7094f7ed6d8a7e587eef2c26af8502185746ac`; PR #132 merged with squash after its required CI passed. PR #131 and post-merge CI `36592558477` also passed.
- Current branch: `feat/workspace-creative-preference`, based on that main commit; implementation and focused checks are local, not yet in a PR.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Its long-term capability reference does not set first-release scope.
- Local synthetic-data product development is authorized. The remaining Phase 0 staging E2E, backup/restore, and rollback checks are release-readiness gates and do not block local product work.
- PR #122 adds a pure fail-closed campaign action-policy evaluator. PR #126 adds two allowlisted synthetic evidence-source labels and caller-supplied timezone-aware observation time. PR #128 adds informational policy version and evaluated-rule identifiers. The 14 focused tests, local Django system check, Ruff checks, PR CI, and post-merge CI passed. These values do not authenticate evidence or persist results.
- PR #131 merged deterministic creative versions into the authenticated campaign flow; source-fingerprint staleness handling and owner-only POST regeneration are covered by CI. Main CI and post-merge CI passed.
- PR #133 adds an owner-scoped review preference for one current creative variant, bound to its version and hidden if source inputs change. A new generated version clears the previous preference. Focused validation: 29 campaign tests and three authenticated campaign browser E2E tests pass on SQLite; Django system check, migration check, Ruff lint and formatting pass. The initial PR CI stopped at a formatting check for the new migration before functional tests; the migration is now formatted and CI is rerunning. PostgreSQL CI has not passed on this branch yet.
- ADR-0014 records the review preference boundary. The options remain synthetic and provider-free; preference is not approval, performance data, or publication.
- The authenticated workspace uses fixed synthetic campaign examples. User uploads, real advertiser/customer/lead data, live account connections, publication, advertiser spend, payments, and production AI are not authorized or implemented.
- Keep the Django/PostgreSQL monolith and approved Heroku staging resources. Add no paid services; never push directly to `main`. Successful PRs may be merged after review and required CI pass under the owner's standing authorization.

## Open risks

- Real-data readiness: secure file handling, privacy/retention, data recipients, provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore, and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- The current evaluator's caller-provided policy evidence is not trusted and is not dispatch authorization. Trusted provenance, any freshness policy, durable audit, atomic budget reservation, and stop/revoke enforcement remain future work.

## Next action

Review PR #133 after its rerun completes. If required CI passes, merge under the user's standing authorization and verify post-merge CI. Keep selection informational and version-bound; do not accept free-text advertiser data or add provider calls.
