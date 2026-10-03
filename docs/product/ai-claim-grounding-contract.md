# AI claim-grounding contract — draft

**Status:** Design draft for review; this is not an accepted ADR or an
authorization to process real customer data. The current website continues to
use deterministic templates. The local Ollama adapter remains disconnected
from product routes.

## Why this draft exists

The synthetic Qwen3 benchmark showed that a response can satisfy the current
JSON and shape checks while copying an unsupported offer from text explicitly
marked as untrusted. Structured output, a matching source hash, and distinct
variant angles establish neither factual grounding nor policy safety. The
exact-phrase benchmark screen is useful for known fixtures only; it cannot
verify arbitrary paraphrases or claims.

## Proposed boundary

Treat advertiser facts and creative claims as separate records. Every fact
considered for copy needs a stable identifier, exact source span or document
location, source/version, owner and permitted use, relevant entity/product,
applicable market/channel, approval state, and any expiry or review date. A
model-proposed claim must identify the fact records it relies on, but those
references are untrusted suggestions until application checks them.

For an offline candidate, allow automatic continuation only when each
factual sentence is either:

1. generated from a deterministic template whose values are drawn from
   approved fact records; or
2. an exact, bounded reuse of approved source wording whose scope and validity
   match the campaign.

An unsupported, ambiguous, expired, revoked, mismatched, or policy-restricted
claim must fail closed. The system should omit the claim and ask the advertiser
for the missing source or clarification when it can continue safely; otherwise
pause the campaign and explain the reason. A model's own citations, confidence,
or a second model's “fact check” are not sufficient proof. Human-facing review
may be useful during offline evaluation, but routine staff approval must not
become a hidden product dependency.

Exact wording is intentionally conservative. Allowing semantic paraphrases
would require a separately validated verifier and a measured false-accept
rate; a language model alone must not provide that guarantee. Health,
financial, legal, outcome, comparative, price/discount, availability, and
other regulated or high-impact claims need explicit policy rules and qualified
review appropriate to the market. This contract does not replace Turkish legal
or platform-policy review.

## Required synthetic evaluation before implementation selection

- Include supported facts, unsupported additions, prompt-injection text,
  contradictory or expired facts, wrong-entity references, and sensitive or
  regulated claim examples across several advertiser types.
- Verify that every supported automatic claim maps to the exact approved fact
  and every unsupported case pauses or omits the claim. Measure false accepts
  separately from false rejects; a zero-false-accept result on a small fixture
  set is only an offline gate, not a safety guarantee.
- Measure useful-copy rate, correction effort, latency, and the extra effort
  asked of beginners and professional advertisers. Preserve source IDs and
  version traceability without exposing private source text in ordinary logs.
- Keep customer-file ingestion, real advertiser data, provider calls from web
  routes, account connections, publication, and spend outside this experiment.

## Open design questions

- What source forms establish advertiser approval and ownership, and how can
  revocation or expiry be reflected before a scheduled campaign runs?
- Which claim classes can be built from deterministic templates and which must
  stop for advertiser input or qualified review?
- How should source provenance be shown to a beginner without burdening the
  professional workflow?
- What evidence and false-accept threshold are required before any broader
  paraphrase verifier can be evaluated?

The next implementation decision should define a persistence-free fact and
claim contract plus a fail-closed synthetic evaluator. It must not claim to
prove semantic truth or authorize publication.
