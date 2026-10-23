# Yaparo rename and local relocation

Verified: 2026-10-23 19:57 Europe/Istanbul (+03:00).

## Current locations

- Product: **Yaparo**, formerly GrowthTwin; owner-requested rename 2026-10-23.
- Source + Git history: `C:\Users\ugrkb\OneDrive\Masaüstü\yaparo`.
- GitHub: https://github.com/ugurkbcgl-hub/yaparo (same repository ID1389718599).
- Python: `%USERPROFILE%\.yaparo\.venv\Scripts\python.exe`, rebuilt and editable-installed
  against the NEW Unicode source path; distribution `yaparo-web`.
- Existing private config/DPAPI stores stay outside OneDrive in their original
  locations. Existing local PostgreSQL database/role remain unchanged.

The old Public Desktop checkout was moved, including .git and working changes;
its now-empty source directory was removed. Old root/web virtual environments,
build outputs and bytecode caches were archived outside sync under the local
Yaparo relocation archive. No .env, SQLite DB, key or DPAPI file was found in the
source inventory moved into OneDrive. Public collected static assets and local
package artifacts can be regenerated; they contain application source/assets.

OneDrive does not use .gitignore as a sync exclusion. Keep runtime, databases,
private config, receipts and keys outside this checkout. `local-python.ps1`
selects the private environment first and refuses repo-venv fallback inside a
configured OneDrive root (or its descendants). Other non-sync checkouts may still
use their conventional local venv. Three local runners use this shared resolver;
no runner was used to call an AI provider as part of renaming.

## Compatibility identities

The public UI/title/accessibility labels, logo, review text download and current
project prose now use Yaparo. Historical ADRs/evidence and these stable technical
identities deliberately continue to contain the former name:

- Python `growthtwin` package, AppConfig/auth classes, app labels and migrations.
- PostgreSQL `growthtwin` database / `growthtwin_app` role.
- `%LOCALAPPDATA%\GrowthTwin\secrets` and `%LOCALAPPDATA%\GrowthTwinsecrets`.
- Envelopes/schema values, hashes/salts, UUID namespaces, immutable receipt/resource
  names, default-off settings, fixed synthetic Google test profile and AI ledger.
- Google Cloud `growthtwin-ads-test`, OAuth client, existing callback URLs, and
  Heroku `growthtwin-stage-270927` remote/deployment identity.

Do not global-replace these IDs or move/reset encrypted material merely to match
branding. No new migration, OAuth consent, account/grant, provider call, deployment
or spend was required. The same GitHub repository was renamed; branch protection
was verified still strict, requiring Django system check, force pushes/deletion
blocked. The origin remote points to the new URL. Old GitHub URLs redirect under
[GitHub's rename behavior](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository).
No GitHub Pages site existed at the time of renaming.

## Pinned private preparation helper

The private helper retains its original bytes/SHA and original legacy REPO
constant. The reviewed loader verifies that SAME source hash first, then accepts
only the current checkout or exact known legacy checkout and its exact0007 file.
Only helper.REPO and helper.MIGRATION are rebound IN MEMORY to the new checkout.
DB, backup, audit and source-hash bindings stay intact. The existing manifest
still verifies the moved migration bytes; unknown roots/paths fail closed.

The actual read-only plan passed from the new checkout: same history/private
backup admitted, permit0/session0, no credential contents read, no current-client
proof and no execute capability. Completed PREPARE/APPLY was NOT rerun. Neither
this relocation nor the plan authorizes new claim, retry/reset or publication.

## Executed relocation checks

- Private editable runtime resolves source to the new checkout and metadata to
  yaparo-web. PowerShell resolver selects that runtime.
- Local PostgreSQL Django check passed; migrate --check and makemigrations
  --check --dry-run reported no pending/schema changes.
- 767-test app suite completed on local SQLite:746 passed,21 PostgreSQL-specific skips;
  separate11 browser E2E tests passed in the new checkout/runtime.
- Four native Windows/PowerShell resolver tests passed: private runtime priority,
  OneDrive child refusal, exact sync-root refusal, non-sync fallback.
- Six pure helper-relocation tests passed, included in app run.
- New yaparo_web wheel and sdist built; required templates/static assets verified.
- GET / and /health/ returned200; homepage has Yaparo and no GrowthTwin label.
- UI review fixed Turkish possessive suffixes. The dev wrapper disables new bytecode
  writes; venv files stay outside source. Static manifest was regenerated after the move.

Fresh fabricated Windows DPAPI match also passed after the move:consumed,2 client/1
candidate reads,session0,history/privateACL/replay/cleanup verified,boundary0.
Final lint/CI outcomes are recorded in TESTING, STATE and PR closure. Real grant/account/publishing readiness remains
unchanged. No external staging deployment was made by this local rename.

## Automation continuity

Existing automation IDs retained, display names and source paths updated through
supported app tools. Both were already paused or time-expired; the23October18:00
work window is now explicitly PAUSED. Do not describe automatic background work
as running or repaired without execution evidence. Current user rename request
is separate authorized work after that old time window.
