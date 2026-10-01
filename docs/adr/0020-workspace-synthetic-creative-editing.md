# ADR-0020: Owner editing for synthetic creative drafts

- Status: Accepted for local synthetic-data development only
- Date: 2026-10-02
- Decision owner: Project owner (delegated implementation decisions)

## Context

Workspace campaigns can create deterministic, provider-free text variants and
remember one informational review preference. The owner needs to revise a
starting draft without replacing its earlier version or implying that the text
has been checked, approved, or published.

## Decision

1. Allow only an authenticated workspace owner to edit a variant on the
   campaign's current creative version through a CSRF-protected POST form.
2. Require a confirmation that the editor contains synthetic example text;
   real advertiser, customer, lead, patient, or other private information is
   outside this workflow.
3. Bound headline, body, and call-to-action text to 80, 240, and 40 characters
   respectively. Reject blank values and stale versions.
4. Append an `owner_edit` version that copies the prior variants and changes
   only the selected variant. Preserve earlier version contents and link the
   new version to its parent. Keep the original campaign source fingerprint so
   later changes to the brief still make the creative stale.
5. Clear the preferred-review selection after editing. Editing does not make a
   selection, approve a claim, establish legal or platform eligibility, call an
   AI provider, upload a file, connect an account, publish, or spend.
6. Keep this feature local and synthetic until the separate real-data
   readiness gate is met.

## Consequences

- Owners can refine a synthetic text draft and inspect prior versions.
- Version history and stale-source checks remain explicit.
- The confirmation and length limits are workflow safeguards, not proof that
  supplied text is synthetic or factually correct.
- Provider generation, claim verification, customer files, real advertiser
  text, publication, and performance testing remain outside this decision.
