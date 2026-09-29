# ADR-0014: Workspace creative review preference

- Status: Accepted for local synthetic-data development only
- Date: 2026-09-29
- Decision owner: Project owner (delegated implementation decisions)

## Context

Workspace campaigns can store versioned, provider-free synthetic copy variants.
An owner needs a simple way to remember which current option they want to
review first. This choice must not be mistaken for approval, publication, or a
performance result, and it must not attach to copy made from changed inputs.

## Decision

1. Store one preferred variant key and creative-version number on the owning
   workspace campaign.
2. Accept the selection only for a known variant in the latest version whose
   source fingerprint still matches the campaign's current brief inputs.
3. Show the preference only while its version is the current, non-stale
   version. A changed source hides the old preference; generating the next
   version clears the previous selection.
4. Keep selection owner-scoped, CSRF-protected, and POST-only. Reject unknown,
   stale, or cross-owner selections.
5. Label the choice as an informational review preference. It is not approval,
   a quality claim, publication authorization, or an external action.
6. Keep this workflow synthetic and provider-free. Do not enable free-text
   advertiser data, file intake, account connections, publishing, or spend.

## Consequences

- Owners can remember one preferred starting point while comparing current
  synthetic options.
- A preference cannot silently carry over to a newer creative version.
- The preference does not establish which creative performs better; no
  audience experiment or engagement measurement is represented.
