# GrowthTwin web application foundation

This folder contains the Phase 0 Django application shell. It is one Django
application with domain module boundaries documented under
`growthtwin/modules/`; those modules intentionally contain no clinic or content
workflow implementation yet.

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
demo user. It has no social publishing, analytics, AI provider calls, or
background workers, and it must use synthetic data only.

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
