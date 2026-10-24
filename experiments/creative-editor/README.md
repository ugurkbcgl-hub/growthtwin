# Yaparo synthetic creative editor experiment

This is the isolated Fabric implementation selected for the bounded local slice by [ADR-0041](../../docs/adr/0041-bounded-fabric-and-brand-identity.md), not a production-ready editor. It does not use Django, databases, accounts, credentials, uploads, APIs, AI or paid resources. Only this directory's explicitly allowlisted static files are served by its loopback helper; the repository is not exposed.

## Run

Use the existing private Yaparo Python environment, which has Playwright installed. From this directory:

```powershell
npm ci --ignore-scripts --omit=optional
& "$env:USERPROFILE\.yaparo\.venv\Scripts\python.exe" serve.py --port 8012
```

Open `http://127.0.0.1:8012/`. The server intentionally accepts only its numeric loopback host/port. Fabric is pinned to 7.4.0 and loaded from the locally installed package; no CDN, hosted editor or frontend build server is required. npm lifecycle scripts and optional packages are excluded. Preserve the lockfile and Fabric license notice in distributions.

The two fixed product/service examples and their bitmap logo/illustration are generated from our canvas drawing code. They are synthetic illustrations, not real photographs or customer assets. Arial comes from the local operating system; no font is downloaded or redistributed. Cross-platform identical font rendering is not claimed.

## Scope and portable format

Editable Turkish title/description, text color and each layer's position/uniform scale/rotation; canvas drag and keyboard-accessible numeric controls; explicit local save/reopen; 800×800 PNG export. Fixed order and four fixed layer identities. This narrow spike does not implement arbitrary uploads, full undo/crop/layer ordering, cross-workspace import, production storage or lossless editor upgrades.

The stored object is Yaparo scene schema v1, **not Fabric JSON**: `schema_version`, fixture, fixed dimensions, bounded layers, asset version identifiers and text/style/transforms. Asset values are identifiers for the fixed fixtures, never URLs. Deserialization validates exact fields, types, fixed IDs/order, color, text and numeric bounds before constructing Fabric objects. Invalid storage is not executed, fetched or overwritten; the clean fixture appears with an error message. A new explicit Save replaces the stored draft. Each fixture has its own localStorage key. Reset loads the clean example in memory; Save is required to overwrite its stored draft.

Saved data exists only in the current browser profile/origin; clearing browser storage loses it. Switching fixtures or resetting asks before discarding unsaved edits. **Do not enter real customer information.** The HTML provides the same notice. Browser editing/export remains available when external network requests are blocked. This is an experiment in local operation, not proof that the whole Yaparo product is offline or production-ready.

## Focused verification

```powershell
& "$env:USERPROFILE\.yaparo\.venv\Scripts\python.exe" test_editor.py
```

For CI, with Python Playwright/browser already installed: `python test_editor.py` from this directory. The suite starts a fresh ephemeral loopback server and fresh browser contexts, blocks and fails on external requests, tests Turkish text/position/save/reload/PNG dimensions, two isolated fixtures/mobile layout, untrusted persisted data, and server path/Host boundaries. No test credentials or databases are used. No Node test runner is required.

## Observed verification — 23 October 2026

Five focused Chromium tests passed locally on Windows using the private Yaparo Python runtime (3.505 seconds test execution, not a user-task benchmark). The PNG was decoded by the browser and verified at 800×800, not merely checked for a filename/header. Title and logo transformations survived reload. Eight malformed saved-state cases were refused, including non-string colors and remote asset references; external request count was zero. Ruff and JavaScript syntax checks passed. npm installed Fabric 7.4.0 alone with optional canvas/jsdom excluded and reported zero audit findings for the installed two-package tree at that time. Desktop and 390px mobile screenshots were visually reviewed outside Git.

The later ADR-0041 rejects the complete-editor candidate at its build/security gate; it does not claim an identical browser-task comparison passed. Full product license/dependency review, performance and upgrade/portability evaluation remain Y06 work. The initial npm audit result is not a complete security review or an adoption decision. No changes to production infrastructure or the main Django application are implied.
