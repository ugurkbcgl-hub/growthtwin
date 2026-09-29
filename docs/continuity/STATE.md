# GrowthTwin — current handoff

Last verified: 2026-09-29 18:41 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Baseline `main`: `fd2c94b398953de7f2a73d4f330425ef5e8257bd`, PR #130 merged with squash. Required CI `36586858121` and post-merge CI `36587154469` passed.
- Current branch: `feat/workspace-creative-variants`, based on the verified main commit. Changes are local and not yet in a PR.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Its long-term capability reference does not set first-release scope.
- Local synthetic-data product development is authorized. The remaining Phase 0 staging E2E, backup/restore, and rollback checks are release-readiness gates and do not block local product work.
- PR #122 adds a pure fail-closed campaign action-policy evaluator. PR #126 adds two allowlisted synthetic evidence-source labels and caller-supplied timezone-aware observation time. PR #128 adds informational policy version and evaluated-rule identifiers. The 14 focused tests, local Django system check, Ruff checks, PR CI, and post-merge CI passed. These values do not authenticate evidence or persist results.
- The current feature branch adds deterministic creative versions to the authenticated campaign flow, source-fingerprint staleness handling, and owner-only POST regeneration. Twenty-five campaign tests, three browser E2E tests, and 29 related creative/policy/asset tests pass on the repository's SQLite test setting; Django check, migration check, Ruff and diff checks pass. PostgreSQL-backed local test DB creation is blocked because the app role lacks CREATEDB; PR CI will verify the suite on PostgreSQL.
- The authenticated workspace uses fixed synthetic campaign examples. User uploads, real advertiser/customer/lead data, live account connections, publication, advertiser spend, payments, and production AI are not authorized or implemented.
- Keep the Django/PostgreSQL monolith and approved Heroku staging resources. Add no paid services; never push directly to `main`. Successful PRs may be merged after review and required CI pass under the owner's standing authorization.

## Open risks

- Real-data readiness: secure file handling, privacy/retention, data recipients, provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore, and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- The current evaluator's caller-provided policy evidence is not trusted and is not dispatch authorization. Trusted provenance, any freshness policy, durable audit, atomic budget reservation, and stop/revoke enforcement remain future work.

## Next action

Finish reviewing `feat/workspace-creative-variants`, run the focused tests/lint and migration checks, then open a PR. The scope is deterministic synthetic creative versions owned by the workspace campaign; keep stale versions hidden and the anonymous demo flow separate. Do not add provider calls, uploads, publication, or spend.
