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

## Persistence-free prototype

The current feature branch adds `apps/web/growthtwin/modules/ai_gateway/claim_grounding.py`.
It evaluates one explicitly listed claim against one fact at a time and accepts
only normalized full-text equality (Unicode NFKC, case folding, and whitespace
collapse) with a non-expired fact record whose owner-approval flag is asserted
by its caller. Unknown or duplicate fact identifiers, unapproved/expired
facts, paraphrases, missing evidence, and oversized values fail closed. The
`source_ref` and version are provenance labels only; they do not prove source
authenticity.

This helper does not discover claims in creative copy or prove that the caller
listed every claim. Its owner-approval flag is not identity-verified. It also
does not establish that a source is true, lawful, current beyond its supplied
expiry date, or permitted by an ad platform. It remains disconnected from all
product routes. Its tests use only fabricated facts and an explicit evaluation
date.

`apps/web/growthtwin/modules/ai_gateway/fact_copy.py` demonstrates bounded
assembly: it joins at most five explicit statements after each exact-match
verdict succeeds, otherwise returning a rejection with verdicts and no text.
It adds no generated connective wording and rejects output over 1,200
characters. This limits additions by the helper but cannot detect omitted
claims in the caller's inventory; it is not a complete creative safety gate.

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

The next implementation decision should demonstrate a deterministic way to
control every factual sentence in assembled copy (for example, fixed safe
templates over exact approved fact text) and evaluate whether it remains useful
on varied synthetic briefs. Do not connect a general generator to routes while
claim inventory completeness is unverified. The prototype must not claim to
prove semantic truth or authorize publication.
