# GrowthTwin web application

This folder contains the Django application, a legacy synthetic profile demo,
and the first local campaign-experience slice. Local product work is authorized
with synthetic data. Domain module boundaries are documented under
`growthtwin/modules/`.

The public `/` route demonstrates one fixed synthetic Ankara home-maintenance
campaign. Visitors can choose an objective, example daily cap, and duration;
there are no free-text brief, brand, or audience inputs. Django saves the fixed
synthetic draft in PostgreSQL, scoped to the anonymous browser session; the
owner can list, resume, edit those plan options, or delete the draft. Drafts
from older versions that do not match the fixed sample stay stored but are
hidden from the public list and cannot be resumed or edited. A
provider-neutral `CampaignBrief` and derived `CampaignPlan` summarize the
example. The draft gets three deterministic, editable copy starting points;
they use only the fixed sample and do not call an AI provider. The page
demonstrates a clearly simulated pause and sample report. It does not connect an
ad account, publish, or spend money. Product-level advertiser intake remains
gated on the real-data readiness work. The session-scoped draft is a prototype
boundary, not a durable advertiser/workspace data model; see
[ADR-0006](../../docs/adr/0006-campaign-brief-boundary.md).

## Runtime prerequisites

- Python 3.13 (the local runtime is 3.13.15).
- Django 5.2 LTS and Psycopg 3 are declared in `pyproject.toml`.
- PostgreSQL 18 is installed locally; Django 5.2 supports PostgreSQL 14 or newer.
- Environment variables set in the process that starts Django:
  - Required: `DJANGO_SECRET_KEY`, `POSTGRES_DB`, and `POSTGRES_USER`.
  - Optional: `POSTGRES_PASSWORD` (defaults to an empty value), `DJANGO_DEBUG`
    (defaults to `false`), `DJANGO_ALLOWED_HOSTS` (defaults to
    `localhost,127.0.0.1`), `POSTGRES_HOST` (defaults to `127.0.0.1`), and
    `POSTGRES_PORT` (defaults to `5432`).
- Staging can instead provide a PostgreSQL `DATABASE_URL`; the app enforces SSL
  for that connection. Configure `DJANGO_ALLOWED_HOSTS`,
  `DJANGO_CSRF_TRUSTED_ORIGINS`, `DJANGO_SECURE_SSL_REDIRECT=true`, and
  `DJANGO_SECURE_COOKIES=true` in the staging provider's config store. Set
  `DJANGO_SECURE_HSTS_SECONDS=3600` for the staging hostname.
- `GET /health/` checks database readiness and reports the deployment revision
  without returning configuration or database details.

No credentials are included in this repository. The application reads settings
from environment variables and does not load `.env` files automatically. The
local setup helper stores its generated Django secret and application password
in the current Windows user's `%LOCALAPPDATA%\GrowthTwin\secrets` directory,
encrypted with Windows DPAPI.

In PowerShell 7, run `scripts\setup-local-postgres.ps1` once. At the hidden
PostgreSQL administrator password prompt, enter the password chosen during
installation. The helper creates the `growthtwin` database and restricted
`growthtwin_app` role, generates a random application password, verifies the
connection, and protects both that password and a generated Django secret with
Windows DPAPI for the current Windows user. Then use
`scripts\dev.ps1 migrate` to initialize Django's framework tables and
`scripts\dev.ps1 runserver` to start the local development server. The helper
loads the locally protected credentials only for the Django process.

The Phase 0 demo contains one profile screen with data scoped to the signed-in
demo user. It has no campaign publishing, analytics, AI provider calls, or
background workers. It must use synthetic data only and should not be mistaken
for the planned advertising product.

## Phase 0 demo

After local database setup and migration, create a local login with
`scripts/dev.ps1 createsuperuser`, then run `scripts/dev.ps1 runserver`. Open
http://127.0.0.1:8000/demo/profile/ and sign in to edit that account’s demo
profile. Each account sees only its own demo profile.

For local demo tests, run
`scripts/dev.ps1 test --settings=config.test_settings`. This uses an in-memory
SQLite database; CI uses an ephemeral PostgreSQL service.

## Python quality checks

Install the application and its pinned development tooling from `apps/web`:

```powershell
python -m pip install -e ".[dev]"
python -m ruff format --check .
python -m ruff check .
python -m pip_audit --local --skip-editable --progress-spinner off
python -m build --sdist --wheel
python scripts/verify_build_artifacts.py
```

Ruff's formatting and lint rules are configured in `pyproject.toml`. To apply
formatting locally, run `python -m ruff format .` and review the resulting diff.
The build command writes distribution files under `build/` and `dist/`; Git ignores both.
