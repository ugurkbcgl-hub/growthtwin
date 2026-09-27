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

There are no custom clinic models, profile screens, publishing or analytics
workflows, AI provider calls, or background workers in this Phase 0 shell.
