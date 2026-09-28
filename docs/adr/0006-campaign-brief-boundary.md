# ADR-0006: Campaign brief ownership and first data boundary

- Status: Accepted
- Date: 2026-09-28
- Decision owner: Project owner (delegated implementation decisions)

## Context

The local prototype now stores synthetic drafts in PostgreSQL, tied to an
anonymous Django session. `CampaignPlan` is a provider-neutral value object in
the `content` module, while the HTTP flow and `CampaignDraft` ORM model remain
in `site`. Treating that prototype row as the future content entity would couple
campaign content to a browser session and make it hard to introduce advertiser
workspaces safely.

## Decision drivers

- Keep domain concepts independent from HTTP, browser sessions, and ORM storage.
- Preserve the working synthetic prototype and its session isolation/deletion.
- Avoid choosing workspace identity, real-data retention, or account lifecycle
  policy before those product/security decisions are ready.
- Keep the request brief distinct from campaign limits and the derived plan.

## Options considered

1. Move `CampaignDraft` and its session foreign key into `content`. This would
   make a domain module depend on an anonymous transport/session mechanism.
2. Create a durable content record now and attach it to the current session.
   This would bake temporary identity and retention assumptions into the future
   data model.
3. Keep the prototype persistence adapter in `site`; define a persistence-free
   brief value in `content`, and defer a content-owned ORM entity until an
   advertiser/workspace owner and retention lifecycle exist.

## Decision

Adopt option 3. The content boundary owns the meaning of the advertiser's
request. `CampaignBrief` contains plain-language text and the optional
objective, audience, and brand/offer context. `CampaignPlan` is derived from
that brief plus proposed campaign limits. Budget boundaries and duration are
planning inputs, not part of the brief itself.

For now, `site` owns form/HTTP behavior and session-scoped synthetic
`CampaignDraft` persistence, and maps that row to content value objects. The
content module must not import Django sessions, requests, or `site` models. No
ORM model move or schema migration is part of this decision.

The site refuses to read a draft when its owning session has expired. Django's
`clearsessions` command removes expired session rows and cascades to drafts;
tests cover that behavior. No recurring invocation is configured in this
repository, so database cleanup timing is unverified. Do not store real
advertiser data until retention and cleanup execution are defined and verified.

Operational re-check on 2026-09-28 found no GrowthTwin-specific Windows
scheduled task. The Heroku Resources page for the existing staging app listed
the Basic web dyno and Essential-0 PostgreSQL, with no Scheduler add-on. The
Heroku CLI is not installed in the local environment. `Procfile` contains only
a `release` migration command and the `web` command. Heroku's release phase runs
when a new release is created, so it is not a recurring cleanup schedule
([Release Phase docs](https://devcenter.heroku.com/articles/release-phase)).

Heroku documents Scheduler as a free add-on, but scheduled tasks run on one-off
dynos whose usage is billed; execution is best-effort and can occasionally be
missed ([Scheduler docs](https://devcenter.heroku.com/articles/scheduler)). A
daily `python manage.py clearsessions` job is a suitable staging cleanup
candidate, not a strict real-data retention guarantee. It has not been
configured. The staging owner's existing approximate USD 12/month approval
does not by itself authorize a new recurring usage pattern; obtain explicit
confirmation before creating a billed scheduled job.

When a persistent content entity is proposed, it must be owned by an explicit
advertiser/workspace identity, not a browser session. Do not implement that
entity until workspace ownership, retention/deletion, and migration/backfill
behavior are specified.

## Consequences

- The brief and plan can be used without a browser request or database row.
- The existing prototype remains session-scoped and synthetic; it is not ready
  for real advertiser data.
- Session expiry blocks access but does not itself prove that expired rows are
  promptly removed. Cleanup cadence is an explicit privacy/operations gate.
- Staging currently has no Scheduler add-on. Scheduler may be useful for
  synthetic staging cleanup, but incurs one-off dyno usage and is not a strict
  scheduler; keep real-data retention blocked until monitoring and a reliable
  policy are defined.
- A candidate staging configuration is `python manage.py clearsessions`, daily
  at 00:00 UTC (03:00 Europe/Istanbul), using the existing Basic dyno type if
  available. This is an estimate/configuration proposal only; it has not been
  provisioned, scheduled, or cost-verified. Current staging approval is about
  USD 12/month, and explicit confirmation is required before enabling variable
  one-off dyno usage.
- A later ORM extraction requires a deliberate data migration and ownership
  transition rather than a direct rename of `CampaignDraft`.
- Workspace identity, retention duration, and real-data acceptance remain open.

## Follow-up

- Keep `CampaignBrief` and `CampaignPlan` free of persistence and HTTP concerns.
- Preserve and verify session isolation, expiry cleanup, edit, and deletion in
  the site adapter.
- If authorized, configure and observe a daily `clearsessions` job for staging
  synthetic data. Do not treat that best-effort job as a production retention
  guarantee.
- Before a content ORM entity or real advertiser data, decide workspace owner,
  retention/deletion policy, and migration/rollback approach.
