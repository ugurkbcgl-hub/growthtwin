# GrowthTwin web application foundation

This folder contains the Phase 0 Django application shell. It is one Django
application with domain module boundaries documented under
`growthtwin/modules/`; those modules intentionally contain no clinic or content
workflow implementation yet.

## Runtime prerequisites

- Python 3.13 (the local runtime is 3.13.15).
- Django 5.2 LTS and Psycopg 3 are declared in `pyproject.toml`.
- A PostgreSQL server supported by Django 5.2 (PostgreSQL 14 or newer).
- Environment variables set in the process that starts Django:
  - Required: `DJANGO_SECRET_KEY`, `POSTGRES_DB`, and `POSTGRES_USER`.
  - Optional: `POSTGRES_PASSWORD` (defaults to an empty value), `DJANGO_DEBUG`
    (defaults to `false`), `DJANGO_ALLOWED_HOSTS` (defaults to
    `localhost,127.0.0.1`), `POSTGRES_HOST` (defaults to `127.0.0.1`), and
    `POSTGRES_PORT` (defaults to `5432`).

No credentials are included in this repository. The application reads settings
from environment variables and does not load `.env` files automatically.

Install the declared dependencies in a suitable Python environment, then use
`python manage.py migrate` to initialize Django's framework tables and
`python manage.py runserver` to start the local development server. These
commands have not been run as part of this skeleton task.

There are no custom clinic models, profile screens, publishing or analytics
workflows, AI provider calls, or background workers in this Phase 0 shell.
