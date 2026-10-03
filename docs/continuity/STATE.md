# GrowthTwin — current handoff

Last verified: 2026-10-03 15:11 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for
advertisers in Türkiye across sectors. Local development and model experiments
remain synthetic-only. Do not enter real advertiser/customer/patient data,
connect live accounts, publish ads, spend media budget, or add paid
infrastructure. Phase 0 recovery, privacy, provider, and platform checks remain
release gates before external beta or production use.

## Verified repository and product state

- PR #221 (`eval/synthetic-creative-benchmark`) merged as
  `32a5cc889d27514e78f960ad6e4d433ac392921c`; PR CI `37120780177` and
  post-merge CI `37120891350` passed. PR #222 (`eval/claim-screen-benchmark`)
  merged as `b464bf1f745b1a68576d4a8f471bbde7ed65db83`; PR CI `37121217179`
  and post-merge CI `37121322397` passed. PR #223 (`design/claim-grounding-contract`)
  merged as `f1158118bf3c7c1d7ce9f369a1015d1ac490107d`; PR CI `37121534148`
  and post-merge CI `37121664437` passed. Current work is on branch
  `feat/synthetic-claim-evidence`; PR/CI status is pending.
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
- A repeatable stdout-only local benchmark runner was added and run on three
  synthetic briefs against Qwen3 1.7B and 4B (one run per cell). All six runs
  were rejected: 1.7B repeated angles in all cases; 4B timed out twice at 120
  seconds and repeated a key once. No output was accepted for usefulness,
  claim-grounding, or review-effort scoring. No model was selected; web routes
  remain on the deterministic template. Results and a future-candidate gate
  are in `AI_PROVIDERS.md`.
- Follow-up included Qwen3 0.6B: two briefs were rejected for invalid keys; an
  initial injection-brief output was structurally accepted but copied the
  untrusted `ücretsiz` offer. Its immediate 9.52-second rerun was rejected for
  duplicate angles. The benchmark runner now reports exact forbidden fixture
  phrases on accepted-shaped output. This is not semantic claim validation;
  no model passed. The website generator remains deterministic.
- A draft claim-grounding contract now describes approved-source provenance,
  exact safe reuse, and fail-closed treatment of unsupported claims. It is not
  an accepted ADR, semantic truth proof, or authorization for real data.
- The current branch adds a persistence-free exact-source claim matcher.
  It checks one caller-listed claim against one owner-approved, non-expired
  fact, rejecting paraphrases and missing/ambiguous evidence. It cannot verify
  source truth, policy, legal compliance, or completeness of the claim list;
  it is not connected to web routes. All 21 focused `ai_gateway` tests and Ruff
  format/lint passed locally with in-memory SQLite test settings.

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

Review and merge the exact-source claim matcher PR after local review and
required CI pass. Then prototype controlled copy assembly over exact approved
fact text and assess its utility on synthetic briefs; keep deterministic
website generation active. Use only synthetic fixtures; leave real data, web-route AI
activation, account connections, publishing, spend, paid services, and the
configured local database untouched.
