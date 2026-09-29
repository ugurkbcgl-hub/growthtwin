# ADR-0013: Workspace synthetic creative versions

- Status: Accepted for local synthetic-data development only
- Date: 2026-09-29
- Decision owner: Project owner (delegated implementation decisions)

## Context

The anonymous website prototype has provider-free copy variants, while the
authenticated workspace campaign flow only shows a local Google Search text
plan. The workspace campaign should let an owner inspect synthetic copy
starting points without conflating them with provider-generated or published
ads. Copy must not appear current after its source brief changes.

## Decision

1. Generate three deterministic copy variants from the workspace campaign's
   brief, brand name, and target city. Keep the anonymous session-owned demo
   separate and unchanged.
2. Persist each generated version as JSON on its owning workspace campaign,
   with an increasing version number, source fingerprint, and creation time.
   Repeated generation against unchanged source is idempotent.
3. Compare the latest version's source fingerprint with current campaign copy
   inputs. If they differ, hide the old text and ask the owner to generate a
   current version; retain history in the campaign record.
4. Do not mark a version stale for budget or flight-date changes, because those
   fields do not influence this deterministic copy function.
5. Keep content synthetic and provider-free. No upload, real advertiser input,
   AI call, platform connection, publication, or spend is added.

## Consequences

- Authenticated owners can review multiple copy angles in the workspace
  campaign flow while the separate anonymous prototype remains isolated.
- The hash only detects changes to selected source fields; it is not a claim
  check, content approval, or proof of truth.
- Provider generation, user editing, approval state, richer format versions,
  and external publication remain later work.
