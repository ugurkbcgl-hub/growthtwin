# GrowthTwin — current handoff

Last verified: 2026-10-03 22:02 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a polished, self-service paid-advertising platform for Türkiye across
industries. The product runtime must not depend on the owner's local PC/GPU.
Develop and evaluate with synthetic data; no real advertiser data, live ad
accounts, publication, spend, or unapproved paid infrastructure.

## Verified repository state at start of this work

- `main` was `e0ec0d949ba5724463ee11aae4e24cf9a3932728`; remote `origin/main`
  matched. The working tree was clean before edits.
- Previous handoff PR #226 is merged. The latest main CI run observed before
  edits was run `37145844015`, success. No open pull requests were returned by
  GitHub at that check.
- Work is on `docs/multi-provider-ai-strategy`, created from the verified
  `origin/main`. Current changes are documentation only; PR/CI are not yet
  created/run at this handoff snapshot.

## Completed in this work

- Reviewed `AGENTS.md`, `PROJECT.md`, `ROADMAP.md`, continuity instructions,
  current state, AI provider history, ADR-0004/0009, and the claim-grounding
  draft. Current product generation is deterministic; Ollama is opt-in and
  disconnected from routes. Recent Qwen3 local evaluation failed the creative
  gate. No production AI provider is selected.
- Checked current official OpenAI, Gemini/Vertex AI, and Anthropic model/API,
  pricing, data handling, media, and model lifecycle pages on 2026-10-03.
- Added `docs/product/ai-provider-strategy.md`: recommends an application-owned
  task router and replaceable hosted providers, with OpenAI/Gemini/Anthropic
  as text candidates and Google/OpenAI as image/video candidates. It describes
  provider/data-class gates, deterministic claim authority, synthetic
  evaluation dimensions, and explicit approval for any billable evaluation.
- Updated `AI_PROVIDERS.md`, `PROJECT.md`, and `ROADMAP.md` to clarify that
  local inference is optional, the website remains on templates, and no
  provider account/API/paid use is activated.
- Refreshed this state snapshot; changes are not yet committed or reviewed by
  CI.

## Current risks and limits

- Provider/model IDs, API features, prices, regions, and terms change. The
  shortlist is not a production recommendation; recheck official terms before
  evaluation or selection.
- OpenAI API content is not used for training by default, but standard abuse
  monitoring may retain data for up to 30 days; video does not support its
  retention controls per the checked docs. Google's free Gemini API may use
  submitted content to improve products; paid service rules differ and still
  include limited safety/legal retention. None of these is a KVKK review or
  confirmation of Türkiye-only processing.
- The owner has not approved a new AI evaluation spend. Existing approximately
  USD 12 Heroku staging approval does not cover provider API charges.
- Existing AI gateway only has a text creative contract and local/synthetic
  adapters. Image/video/document integrations, task routing, real-data
  readiness, and provider availability failover are not implemented.
- Current hosted/API vendor performance has not been measured on GrowthTwin's
  own task suite. No candidate may receive real advertiser material or be
  connected to routes based on these documents alone.

## Next action

Review and merge the documentation PR after required CI passes. Then implement
provider-neutral task profiles and a repeatable synthetic benchmark interface
for the text shortlist without provider credentials or web-route calls. Ask
for a bounded spend decision only when a live, billable vendor comparison is
actually required; keep image/video and customer-file ingestion behind their
separate readiness gates.
