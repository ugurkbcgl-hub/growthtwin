# GrowthTwin — current handoff

Last verified: 2026-10-04 17:55 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a self-service paid-advertising platform for Türkiye across industries.
Continue local synthetic product development. No real advertiser data, live ad
accounts, publication, media spend, or production AI use.

## Repository and CI state

- PR #250 merged as `2ab4ea4`; required PR CI `37210497789` and post-merge CI
  `37210643009` passed. Recheck branch and open PR state before acting.
- Its Gemini-only 1,024-token cap let three synthetic calls complete, but the
  fourth response ended at 1,009 tokens with `finish_reason=length`; the runner
  stopped and sent no further calls.
- Current feature branch proposes 1,536 output tokens for Gemini, retains 512
  for GPT-6 Luna, and keeps every request's upper reservation below USD 0.01.
  Local focused tests, estimate, lint, and formatting passed on the merged
  1,024-token version. Rerun the focused checks after the cap change, then
  review PR/CI; do not call the provider until required CI succeeds.

## AI/provider status

- Deterministic website templates remain active; no provider is connected to
  product routes and no production model is selected.
- OpenRouter dashboard logs match the Gemini run's four Vertex upstream calls
  at HTTP 200. Three returned `stop` with 653/873/830 tokens; one returned
  1,009 tokens and `length`, cost USD 0.00414. The local reservation for that
  failed-closed call was reconciled to the matching log. Five calls remained
  unsent.
- The three completed synthetic home-maintenance repetitions had no configured
  forbidden-phrase match. Manual assistant review found generic, similar-angle
  copy and one unsupported immediacy word; provisional scores: usefulness 3/5,
  grounding 4/5, diversity 2/5, brand fit 3/5, correction effort 2/5. The
  two other synthetic briefs are unevaluated; this does not pass the candidate
  gate.
- Shared local evaluation ledger: USD 0.0242432 spent, USD 0.00078075 reserved
  for an unrelated earlier GPT call. These are not live account credits.
- Read-only account inspection verified the approved USD 16 API-key cap with no
  reset. Do not record account balance/usage or change account settings.

## Risks and boundaries

Use only the fixed synthetic cases; `zdr=true` and `data_collection=deny` do
not establish Türkiye/EU processing or KVKK compliance. No credit top-up or
auto-recharge, private data, live ad-account connection, publication, media
spend, or AI product-route use. Keep key and local-ledger safeguards intact.
Never store credentials or provider output in Git.

## Next action

Verify PR #251 and its required CI. If successful, merge under the owner's
standing authorization, wait for post-merge CI, then run the one fixed
nine-call evaluation with the 1,536 Gemini token cap. Stop at the first
truncated/unverifiable response, leave further calls unsent, and reconcile
reservations only against matching provider cost evidence. If all nine finish,
manually assess outputs from all three synthetic briefs; do not select a
production provider from one run. Keep USD 0.00078075 for the unrelated GPT
call reserved until its own log is reconciled.
