# ADR-0007: Workspace ownership and campaign data lifecycle

- Status: Accepted for local synthetic-data development only
- Date: 2026-09-29
- Decision owner: Project owner (delegated implementation decisions)

## Context

Phase 1 now meets its local prototype acceptance criteria. Phase 2 calls for
advertiser/workspace-owned campaign data, while [ADR-0006](0006-campaign-brief-boundary.md)
keeps the existing anonymous session draft outside the future content model
until ownership, retention/deletion, and migration behavior are specified.

The current prototype stores synthetic drafts in PostgreSQL through Django
sessions. Session expiry blocks access, and `clearsessions` can remove expired
records, but the scheduled staging cleanup is best-effort and is not a real-data
retention guarantee.

## Decision

1. **Tenant boundary:** a workspace is the owner of future campaign, brand, and
   creative records. The first local model may use an authenticated Django user
   as its owner. Access must be authorized server-side through that ownership
   or an explicit membership; a browser session is never the tenant authority.
   Additional members and roles can be added when collaboration requirements
   are implemented.
2. **Prototype data:** use synthetic data only. Existing anonymous session
   drafts remain prototype records in `site`; they are not content ORM entities.
   Do not use the local/staging model to accept real advertiser, customer, or
   patient data.
3. **Retention and deletion:** do not assign one universal retention duration
   to all advertiser data. Before real data is accepted, inventory each data
   category and purpose, applicable processing basis and obligations, recipients,
   maximum retention, deletion method, and backup behavior. Until then, the
   production retention policy remains unresolved and real-data processing is
   blocked. Keep the current session-draft expiry and synthetic staging cleanup
   accurately described as access expiry and best-effort cleanup.
4. **Migration and backfill:** never attach anonymous session drafts to a
   workspace automatically. No backfill is needed for the initial local model.
   Any later explicit transfer must establish the authenticated owner and be
   covered by a transaction, backup, and tested rollback before staging use.
5. **Release gate:** tenant-isolation tests, data export/deletion behavior,
   category-specific retention, privacy review, backup/restore, and rollback
   must be verified before real advertiser data or an external beta.

This is a technical boundary for synthetic local development. It is not a legal
assessment or approval to process personal data. KVKK materials describe
retention in relation to purpose and applicable obligations; they do not supply
one GrowthTwin-wide duration. See the [KVKK deletion and destruction
regulation](https://www.kvkk.gov.tr/Icerik/5441/KISISEL-VERILERIN-SILINMESI-YOK-EDILMESI-VEYA-ANONIM-HALE-GETIRILMESI-HAKKINDA-YONETMELIK)
and the Authority's [FAQ on retention for the necessary period](https://kvkk.gov.tr/SharedFolderServer/CMSFiles/c148901d-cd7f-43ff-ae9a-978fb78fb43c.pdf).

## Consequences

- Phase 2 can add local synthetic workspace-owned models without reusing the
  anonymous session row as the future campaign entity.
- No automatic migration or account-claim flow is needed for existing synthetic
  drafts.
- Production identity, legal bases, category-level retention durations,
  deletion/export obligations, provider data terms, and real-data admission
  remain explicit release decisions.

## Follow-up

- Implement the smallest local synthetic workspace-owned record only after
  adding tenant-ownership and deletion tests.
- Keep the session-owned `CampaignDraft` path unchanged until there is an
  explicit user-facing account/workspace flow and a separately reviewed data
  lifecycle policy.
