# GrowthTwin — current handoff

Last verified: 2026-10-03 14:26 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for
advertisers in Türkiye across sectors. Local development and model experiments
remain synthetic-only. Do not enter real advertiser/customer/patient data,
connect live accounts, publish ads, spend media budget, or add paid
infrastructure. Phase 0 recovery, privacy, provider, and platform checks remain
release gates before external beta or production use.

## Verified repository and product state

- `main` is clean at `56ecad7b66e95379d0392688acf1d9ca5f91805c`. PR #217, #218,
  and #219 are merged; no PRs were open at the verification time. Required PR
  CI and post-merge CI passed: #217 (`37117805803`, `37117931162`), #218
  (`37118174068`, `37118316828`), and #219 (`37119217743`, `37119348560`).
- The `ai_gateway` now has an immutable provider-neutral request/result
  contract, fail-closed structured-output/length/source/key/diversity checks,
  and a deterministic synthetic adapter. Both public fixed-sample and
  authenticated workspace copy flows use that template adapter. Workspace
  versions record the generator id and preserve it through edits/restores.
- An opt-in `OllamaCreativeGenerator` is limited to direct loopback HTTP, with
  no proxy, redirect, credential, or streaming behavior. It is not connected to
  web routes. Generated results remain review-required and non-publishable.
  `synthetic_only` is a caller assertion, not authorization to process real
  data.
- Local validation on 2026-10-03: 75 focused Django tests passed using the
  in-memory SQLite test settings; Ruff lint and format checks passed. One
  Qwen3 1.7B structured-output run took about 30 seconds and returned repetitive
  copy with an unsupported phrase. One Qwen3 4B run took about 80 seconds and
  was rejected for repeating variant angles. Neither model is selected for
  product use; the website continues to use the deterministic template.
- Ollama 0.35.1 and Qwen3 0.6B/1.7B/4B were already installed; no model was
  downloaded. The exact Qwen3 1.7B tag's Ollama library page lists Apache-2.0;
  this is not legal review. Evaluation details and official references are in
  [AI_PROVIDERS.md](../../AI_PROVIDERS.md).

## Open risks and limits

- Heroku staging was last checked earlier on 2026-10-03 at 13:37 +0300; release
  v18 pointed to the v16 rollback target. Staging was not changed or rechecked
  during this local AI work. That rollback tested same-application-code only;
  configured-database recovery and rollback across code/schema changes remain
  unverified.
- Heroku billing last displayed $0.00 current usage and a $1.37 September
  invoice marked Pending; neither is a final cost. Tax and Scheduler one-off
  cost remain unknown.
- The configured local `growthtwin` inventory had one test-marked account, no
  demo profiles, eight anonymous drafts not matching the current sample, nine
  sessions, and one workspace campaign with stored creative versions. Older
  drafts and creative values remain unclassified. No data-bearing dump/restore
  was attempted; this AI work did not touch the configured PostgreSQL database.
- A stopped synthetic PostgreSQL rehearsal folder remains in `%TEMP%`; cleanup
  was blocked by tool policy and no alternate deletion method was attempted.
- Session cleanup is best-effort, not a real-data retention guarantee. Keep
  local/staging content synthetic. There is still no platform account, API,
  publication, spend, live forecast, or verified report source.
- The Qwen3 results are one-run smoke tests, not quality or safety evidence.
  Schema correctness does not establish factual grounding, legal/platform
  compliance, or useful creative quality.

## Next action

Define and run a repeatable synthetic creative-quality benchmark across several
brief types and candidate models. Score usefulness, claim grounding, variant
diversity, schema validity, latency, and review effort; keep the current
deterministic website generator in place until a candidate meets explicit
criteria. Re-read `AI_PROVIDERS.md` before model/provider changes, use only
synthetic fixtures, and leave real data, web-route AI activation, account
connections, publishing, spend, paid services, and the configured local
database untouched.
