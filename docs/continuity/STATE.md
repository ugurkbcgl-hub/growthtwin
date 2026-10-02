# GrowthTwin — current handoff

Last verified: 2026-10-03 00:50 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for
advertisers in Türkiye across sectors. Local product work remains synthetic.
Do not use real advertiser/customer/patient data, connect live accounts,
publish ads, spend media budget, add paid infrastructure, or alter staging.
Phase 0 recovery, privacy, provider, and platform checks remain release gates
before an external beta or production use.

## Verified repository state

- `main` is at `6966c4beb8677c813bac92bf2c799bda6fc81596` after PR #197.
  PR #197 required CI (`37068418385`) and post-merge `main` CI
  (`37068642570`) both passed. No open PRs were listed; the local `main`
  checkout was clean. Verify these live facts again next session.
- Public intake code from PR #195 is at
  `7647d113321890d958a4d80efd4b9cc954af4ed7`; its PR check
  (`37066810561`) and post-merge `main` CI (`37067055104`) both passed. PR #196
  then merged the continuity update at
  `8cd18a8f41c8e50f8b3d728e639c00fce81094ee`; its required CI
  (`37067463258`) and post-merge `main` CI (`37067699932`) both passed.
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

The authenticated workspace creative-editing flow was audited against the
synthetic-only boundary. Its owner scoping, CSRF-protected POST, server-side
length limits, append-only versions, and provider-free behavior are adequate
for local synthetic prototyping. The confirmation is not proof of synthetic
content and does not make the flow ready for real advertiser data. Existing
limits are recorded in ADR-0020 and PROJECT.md; no code or canonical policy
change was needed. No implementation is currently in progress.

## Next action

Refresh `docs/product/current-system-gap-analysis.md` against the current
`main` implementation and accepted product decisions. Use it to choose the
next small local, synthetic UX improvement; do not open real-data intake,
connect live services, or change product scope.
