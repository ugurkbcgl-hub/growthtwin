# ADR-0002: Application stack and local development environment

- Status: Accepted
- Date: 2026-09-27
- Decision owner: Project owner

## Context

GrowthTwin needs a web panel for clinic workspaces, content drafts and versions, review/approval, and eventually social publishing and analytics. Phase 0 currently allows only a synthetic-data profile-edit demo. ADR-0001 accepts a modular monolith; hosting and supporting technology choices remain open.

Current workstation evidence: Windows 11; Ubuntu is installed under WSL2 (WSL package 2.6.1.0; distro was stopped when checked); Node.js 24.11.1 and npm 11.6.2 are available on Windows; Python 3.13.15 and PostgreSQL 18.6 with `psql` are installed on Windows. The Codex-managed Git checkout is on the Windows filesystem. Do not create a second working checkout in WSL without first confirming the Codex workspace can use it as the single source of truth.

NVIDIA NIM and Ollama can both be accessed over HTTP, so the choice of app language does not determine which provider can be integrated. Hosted NIM remains evaluation-only, with synthetic data.

## Decision drivers

- Keep Phase 0 and the first product implementation to one application/runtime where practical.
- Support a custom clinic-facing content and approval panel, not only an internal administration screen.
- Keep AI providers behind a server-side adapter and keep credentials out of browsers.
- Use the existing Codex-managed checkout and avoid new monthly infrastructure costs.
- Preserve explicit tenant isolation and exact-version approval requirements regardless of framework.

## Options considered

### A. Django 5.2 LTS + PostgreSQL — recommended proposal

One Python application with Django templates/forms and the built-in authentication, permissions, and administration facilities. Organize its modules around workspaces/access, content/versioning, approval, publishing, analytics, and the AI gateway. The admin is for internal operations; clinic users receive purpose-built screens in the same application.

**Why this is the proposed default:** the first product workflows are records, roles, review states, and approvals. Django provides a mature path for those data-oriented workflows in one application, while Python leaves a straightforward option for future media/model tooling. Django's built-in authentication and admin can shorten internal setup, though tenant-specific authorization still needs careful application rules. NIM and Ollama integrations remain ordinary HTTP adapters.

**Trade-offs:** Python 3.13.15 is installed on the current Windows host, but the application still needs its project-specific virtual environment and dependencies set up. Django avoids starting two product application runtimes. Django's admin is not the clinic-facing content editor; those screens still need custom design. Django 5.2 LTS supports PostgreSQL 14+ and has extended support through April 2028.

### B. Next.js App Router + TypeScript + PostgreSQL

One full-stack application under `apps/web`. Node.js 24.11.1 and npm 11.6.2 are already available on the Windows host; Next.js supports Windows/WSL and its starter includes TypeScript defaults. This is the fastest route to the M4 profile demo and gives a React-based interface suited to a highly interactive editor.

**Trade-offs:** Next.js server functions and route handlers are a backend-for-frontend layer, not a complete replacement for a deliberately designed backend. We would need to explicitly choose authentication/session handling, authorization, persistence access, migrations, and tenant scoping. NIM and Ollama can be reached over HTTP from a Node.js application. Scheduled publishing would need a durable background worker regardless of framework.

### C. Next.js + FastAPI + PostgreSQL

This follows the project's original reference candidate and separates the React UI from a Python API. It remains viable if a separate API boundary or Python-only processing becomes necessary.

**Trade-offs:** it creates two application runtimes, two deployable components, and an API contract to maintain before the first demo demonstrates a need for that split.

## Accepted decision

On 2026-09-27, the project owner accepted **Django 5.2 LTS + PostgreSQL** as the initial application stack, with one application under `apps/web` and a modular monolith structure. Use the latest supported 5.2.x security patch when installing. Use the currently supported stable PostgreSQL major at implementation time and verify the chosen staging provider supports it. PostgreSQL 18 is current as of this decision and receives upstream major-version support for five years.

For local development, keep the repository at its current single Windows checkout. Use the installed supported Python runtime rather than creating a second WSL copy that could diverge from the Codex workspace. PostgreSQL 18.6 is installed locally and is used for development. Docker Desktop is not required for the app runtime; do not install it unless its license eligibility is confirmed. No remote development server, staging service, or paid resource is needed for this local setup.

### Local environment update — 2026-09-27

- PostgreSQL 18.6 is running as the local `postgresql-x64-18` Windows service on port 5432.
- The `growthtwin` database and restricted `growthtwin_app` role are set up; app credentials are generated and protected with Windows DPAPI outside the repository.
- The Django framework migrations and system check completed successfully.
- The helper scripts are documented in `apps/web/README.md`. This update does not authorize product features, staging deployment, or paid services.

CI uses a GitHub-hosted standard Ubuntu runner through `.github/workflows/ci.yml`. The `Django system check` is required on protected `main`, and pull requests must be up to date with `main`; these repository settings were verified on 2026-09-27. Do not use the laptop as a self-hosted runner.

Defer Redis, Temporal, pgvector, object storage, and a worker until an accepted feature requires them. Keep publishing/scheduling outside the M4 demo. The AI gateway may call local Ollama or a hosted trial provider through server-side adapters; hosted trials receive synthetic evaluation inputs only and do not serve end users.

This decision authorizes the Phase 0 Django foundation only. It does not authorize GrowthTwin product features, production deployment, real clinic/social account data, or paid infrastructure.

## Consequences

- The product begins with one runtime, one application, and one primary database.
- Django's admin can support internal operations, while clinic workflows remain purpose-built product screens.
- Authentication primitives are available, but tenant-level authorization and workspace isolation still require deliberate design and verification.
- A future scheduler may need a worker process, but can remain in the same repository and share domain modules.
- The installed Node runtime remains available for tooling, but it is not required for the proposed server-side application.
- The staging provider, database hosting, and project cost ceiling remain open.

## Official references checked 2026-09-27

- [Django 5.2 release notes and PostgreSQL support](https://docs.djangoproject.com/en/5.2/releases/5.2/)
- [Django supported versions and support periods](https://www.djangoproject.com/download/)
- [Django authentication and permissions](https://docs.djangoproject.com/en/5.2/topics/auth/)
- [Django administration site](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/)
- [Next.js installation and system requirements](https://nextjs.org/docs/app/getting-started/installation)
- [Next.js Backend-for-Frontend guidance](https://nextjs.org/docs/app/guides/backend-for-frontend)
- [Next.js authentication guidance](https://nextjs.org/docs/app/guides/authentication)
- [Node.js release schedule](https://nodejs.org/en/about/previous-releases)
- [PostgreSQL versioning and support policy](https://www.postgresql.org/support/versioning/)
- [Microsoft WSL file-system guidance](https://learn.microsoft.com/en-us/windows/wsl/filesystems)
- [GitHub Actions billing and public repository usage](https://docs.github.com/en/actions/concepts/billing-and-usage)
