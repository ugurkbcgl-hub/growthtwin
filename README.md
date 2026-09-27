# GrowthTwin

GrowthTwin is a self-service advertising website for individuals, creators, and businesses. Its goal is to carry an advertiser's request through campaign planning, creative production, safe checks, authorized publishing, and understandable performance reporting with as little effort from the user as possible. Routine work should not require a GrowthTwin operator; automation must stay within the advertiser's explicit account, schedule, content, and spend limits.

Product development now focuses on a local, synthetic-data website prototype. The previous clinic profile-edit app is only a development/staging check. Dental clinics remain a possible early pilot cohort, while the product itself should support different advertiser types.

The existing stack is Django 5.2 LTS + PostgreSQL in one modular monolith. No production AI provider, publishing platform, production host, or additional paid service has been selected. See [PROJECT.md](PROJECT.md), [ROADMAP.md](ROADMAP.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [the ADR index](docs/adr/README.md) for the current direction and boundaries.

Use the single checkout at `C:\Users\Public\Desktop\GrowthTwin`, feature branches, pull requests, and the existing CI workflow. Local prototypes and hosted model experiments must use synthetic data. The approved Heroku app is limited to Phase 0 staging and is not a production or AI serving environment.

To resume in another chat, read the required project files in the order documented by [the continuity guide](docs/continuity/README.md), then verify the current Git and CI state before acting.
