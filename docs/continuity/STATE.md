# GrowthTwin — current handoff

Last verified: 2026-10-03 22:08 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a polished, self-service paid-advertising platform for Türkiye across
industries. Product runtime and AI quality must not depend on the owner's
local PC/GPU. Develop with synthetic data; no real advertiser data, live ad
accounts, publication, media spend, or unapproved paid infrastructure.

## Repository and work status

- `main` was verified at `b2e63d6deee31bef7bb4d192a7aedbe6e4b2f5c6`, the
  merge commit for PR #227. PR #227 merged successfully; required PR CI
  `37146525709` and post-merge main CI `37146671062` passed, including tests
  and browser E2E.
- No open PRs were returned after #227 merged. A documentation-only state
  refresh is being prepared on `docs/update-ai-provider-handoff`, based on
  that main commit; verify its current PR/CI status at the next session.
- The strategy changes themselves are in [AI provider combinations](../product/ai-provider-strategy.md),
  and are documented in `AI_PROVIDERS.md`, `PROJECT.md`, and `ROADMAP.md`.

## AI and product status

- Current website generation remains deterministic. The provider-neutral
  gateway has a text creative contract and synthetic/local adapters; Ollama
  is optional and disconnected from routes. Recent Qwen3 evaluations failed
  the existing small creative gate. No production provider is selected.
- The new recommendation is a task router, not a local inference dependency
  or one-vendor lock-in. Candidate set: OpenAI, Google Gemini/Vertex AI, and
  Anthropic for text; Google and OpenAI for image and short-video generation.
  This is a research/evaluation shortlist, not permission to activate APIs or
  spend money.
- The provider strategy was checked against official vendor model/API, data,
  terms, and pricing pages on 2026-10-03. Recheck exact model IDs, data
  retention, region, availability, and pricing before any use. No live API
  comparison has been run.
- Existing approximately USD 12 Heroku staging approval does not cover AI
  provider charges. No new provider account, credential, paid quota, or
  service was activated.
- Image/video/document integrations, task routing, provider failover, and
  real-data readiness remain unimplemented. Deterministic source/claim rules
  stay authoritative; model review alone cannot clear claims or ads.

## Risks and gates

- Free Gemini API use may expose submitted content to product improvement and
  human review; paid service terms differ and still permit limited safety/legal
  processing. OpenAI's general API controls and Video API retention differ by
  endpoint. These are not KVKK approval or Türkiye-only data residency
  guarantees. No real advertiser material may be sent.
- Any billable hosted evaluation requires a separate bounded owner-approved
  budget and synthetic fixtures. Do not connect provider calls to user routes
  until task gates and privacy/data readiness are met.
- Keep asset intake, ad-account connection, publishing, spend, and production
  deployment behind their existing approval/readiness gates.

## Next action

Implement provider-neutral task profiles and a repeatable, credential-free
synthetic benchmark interface for the text shortlist. Keep the website on its
deterministic template and provider calls out of routes. Request a bounded
evaluation budget only when live billable comparisons are required; evaluate
image/video and customer-file paths later behind their own readiness gates.
