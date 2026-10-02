# GrowthTwin — current handoff

Last verified: 2026-10-03 00:29 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for
advertisers in Türkiye across sectors. Local product work remains synthetic.
Do not use real advertiser/customer/patient data, connect live accounts,
publish ads, spend media budget, add paid infrastructure, or alter staging.
Phase 0 recovery, privacy, provider, and platform checks remain release gates
before an external beta or production use.

## Verified repository state

- `main` is at `7647d113321890d958a4d80efd4b9cc954af4ed7`, merged via PR #195.
  The PR check (`37066810561`) and post-merge `main` CI (`37067055104`) both
passed. The local `main` checkout was clean, and no open PRs were listed.
- PR #195 closes the public free-text intake gap: the visitor can choose an
  objective, example budget, and duration for one fixed synthetic Ankara
  home-maintenance scenario. The server ignores posted brief/brand/audience
  text and never persists it. Earlier session drafts that do not match the fixed
  sample remain stored but are hidden and cannot be resumed or edited; they
  were not deleted or rewritten.
- Local verification passed: all 120 Django tests, all 3 mobile campaign E2E
  tests, Django system check, Ruff formatting/lint, and `git diff --check`.
  Tests used an in-memory SQLite database; CI used its ephemeral PostgreSQL
  service. No migration, AI/provider, platform, staging, publication, or spend
  change was made.
- The updated public page at `http://127.0.0.1:8002/` was inspected in the
  browser. It shows the fixed example, no free-text brief/brand/audience fields,
  and a notice that older drafts may remain stored but are hidden. The local
  development server is running on port 8002.
- PR #192's campaign-detail readiness explanation remains in place; its
  required and post-merge checks passed (`37061846991`, `37062126477`).

## Open risks and limits

- Older anonymous session drafts from versions that accepted free text are
  hidden but retained. Session expiry and `clearsessions` are best-effort, not
  a verified real-data retention guarantee. The old rows were not queried
  directly or changed; their provenance is unknown.
- Heroku release v14 (`69476a62`) and `/health/` revision `unknown` were last
  recorded on 2026-10-01; recheck live staging before any staging work.
- Configured-database recovery and controlled staging rollback remain
  unverified. An isolated PostgreSQL rehearsal folder remains from prior work;
  do not attempt alternate deletion paths. Staging charges and Scheduler's
  one-off cost remain unverified.

## Current work

This continuity refresh is PR #196 on `docs/continuity-after-pr-195`; it is
not sent directly to `main`. Verify its required CI before merging under the
owner's standing authorization for successful PRs.

## Next action

Audit the authenticated workspace creative-editing flow against the same
synthetic-data readiness boundary. Keep it provider-free and workspace-scoped;
decide whether its existing synthetic-only confirmation and copy-edit limits
are sufficient, without entering real advertiser data or changing live
services.
