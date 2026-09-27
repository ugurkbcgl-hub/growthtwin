# ADR-0003: Heroku Phase 0 staging

- Status: Accepted
- Date: 2026-09-27
- Decision owner: Project owner (approved the provider and budget)

## Context

Phase 0 requires a persistent staging deployment of the synthetic Django demo, with PostgreSQL, a repeatable deployment path, health/readiness checks, E2E coverage, backups, and rollback verification. The selected local and CI database major is PostgreSQL 18.

## Decision drivers

- Keep the staging stack close to Django 5.2, Python 3.13, and PostgreSQL 18.
- Keep recurring cost near the owner's approved USD 12/month staging budget.
- Avoid sleeping app compute during E2E checks and keep the database long enough to repeat the Phase 0 workflow.
- Do not use real clinic, patient, lead, or customer data.

## Options considered

1. Heroku Basic web dyno + Essential-0 PostgreSQL — predictable base estimate of USD 12/month before taxes; supports PostgreSQL 18; the Basic dyno remains available for E2E checks.
2. Render free web service + Postgres — no base compute charge, but the web service sleeps and the free database expires after 30 days without backups.
3. Railway Hobby — USD 5/month minimum with metered resources, so the final total is less predictable than the approved plan.

## Decision

Use Heroku for Phase 0 staging with one Basic web dyno and one Essential-0 PostgreSQL 18 database in the EU region. The owner approved this plan at about USD 12/month before taxes on 2026-09-27. Do not provision paid add-ons or additional dynos without a new owner decision. Keep all data synthetic and keep production out of scope.

## Consequences

- Base recurring cost is about USD 12/month before taxes, comprising the Basic dyno and Essential-0 database. No other recurring resource is included in this decision.
- The Essential-0 database has limited storage and connections; this is sufficient for the synthetic Phase 0 demo, not a production selection.
- Heroku config vars hold the Django secret and host/security settings; the database add-on supplies `DATABASE_URL`.
- Enforce HTTPS, secure cookies, and one-hour HSTS for the staging hostname. Do not extend HSTS to subdomains or request preload for this temporary staging host.
- Heroku's release phase will apply migrations before the new app release becomes active. Build and deployment artifacts must be tied to reviewed source.
- Charges continue until the Heroku app and database are deleted. Delete both after M4 acceptance.
- EU Common Runtime placement does not guarantee all Heroku processing stays in that region; use synthetic data only.
- Do not use real customer or patient data, connect clinic accounts, or deploy production workloads.

## Follow-up

- Add Heroku runtime, security, database, static-file, migration, and readiness configuration through a reviewed PR.
- Provision the approved resources after account authentication is available.
- Verify deployment, Playwright profile editing, readiness/version output, backup/restore, and rollback; record actual costs and results in the Phase 0 report.

## References

- [Heroku pricing](https://www.heroku.com/pricing/)
- [Heroku Postgres plans](https://devcenter.heroku.com/articles/heroku-postgres-plans)
- [Heroku Postgres version support](https://devcenter.heroku.com/articles/heroku-postgres-version-support)
- [Heroku Python support](https://devcenter.heroku.com/articles/python-support)
- [Heroku regions](https://devcenter.heroku.com/articles/regions)
- [Render free-tier limits](https://render.com/docs/free)
