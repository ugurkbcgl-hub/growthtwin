"""Windows runtime selection uses fabricated executables and an isolated profile."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest import skipUnless

from django.test import SimpleTestCase

_PWSH = shutil.which("pwsh")
_SELECT_RUNTIME = r"""
$ErrorActionPreference = 'Stop'
$data = [Console]::In.ReadToEnd() | ConvertFrom-Json
$env:USERPROFILE = $data.profile
$env:OneDrive = $data.sync
$env:OneDriveCommercial = ''
. $data.helper
try {
    $selected = Get-YaparoPython -WebRoot $data.web
    @{status='selected';path=$selected} | ConvertTo-Json -Compress
} catch {
    @{status='refused';path=''} | ConvertTo-Json -Compress
}
"""


@skipUnless(os.name == "nt" and _PWSH, "Windows and PowerShell 7 are required")
class LocalRuntimeSelectionTests(SimpleTestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="yaparo-runtime-fixture-")
        self.root = Path(self.temporary.name).resolve()
        self.parent = self.root.parent.resolve()
        self.addCleanup(self.cleanup_owned_fixture)
        self.profile = self.root / "fabricated-profile"
        self.sync = self.profile / "OneDrive"
        self.synced_web = self.sync / "fabricated-repo" / "apps" / "web"
        self.unsynced_web = self.root / "fabricated-local-repo" / "apps" / "web"
        self.helper = (
            Path(__file__).resolve().parents[3] / "scripts" / "local-python.ps1"
        )
        self.assertTrue(self.helper.is_file())
        self.synced_web.mkdir(parents=True)
        self.unsynced_web.mkdir(parents=True)

    def cleanup_owned_fixture(self):
        # TemporaryDirectory owns only this newly created, captured temporary root.
        current = Path(self.temporary.name).resolve()
        self.assertEqual(current, self.root)
        self.assertEqual(current.parent, self.parent)
        self.assertEqual(self.parent, Path(tempfile.gettempdir()).resolve())
        self.assertTrue(current.name.startswith("yaparo-runtime-fixture-"))
        self.assertFalse(current.is_symlink())
        self.temporary.cleanup()

    def fake_python(self, root):
        path = root / ".venv" / "Scripts" / "python.exe"
        self.assertTrue(path.is_relative_to(self.root))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"fabricated executable placeholder; never executed")
        return path

    def select(self, web):
        environment = {
            key: os.environ[key]
            for key in ("SystemRoot", "WINDIR", "COMSPEC", "PATH", "TEMP", "TMP")
            if key in os.environ
        }
        environment.update(
            USERPROFILE=str(self.profile),
            HOME=str(self.profile),
            LOCALAPPDATA=str(self.profile / "AppData" / "Local"),
            APPDATA=str(self.profile / "AppData" / "Roaming"),
            OneDrive=str(self.sync),
            OneDriveCommercial="",
        )
        completed = subprocess.run(
            [
                _PWSH,
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                _SELECT_RUNTIME,
            ],
            input=json.dumps(
                {
                    "profile": str(self.profile),
                    "sync": str(self.sync),
                    "helper": str(self.helper),
                    "web": str(web),
                }
            ),
            text=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
            timeout=20,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        self.assertEqual(completed.returncode, 0, "Runtime selector process failed")
        self.assertEqual(completed.stderr, "")
        return json.loads(completed.stdout)

    def test_private_runtime_is_preferred_even_when_synced_repo_has_fallback(self):
        private = self.fake_python(self.profile / ".yaparo")
        self.fake_python(self.synced_web)
        self.assertEqual(
            self.select(self.synced_web), {"status": "selected", "path": str(private)}
        )

    def test_synced_repo_refuses_fallback_without_private_runtime(self):
        self.fake_python(self.synced_web)
        self.assertEqual(
            self.select(self.synced_web), {"status": "refused", "path": ""}
        )

    def test_unsynced_repo_accepts_local_web_runtime_fallback(self):
        fallback = self.fake_python(self.unsynced_web)
        self.assertEqual(
            self.select(self.unsynced_web),
            {"status": "selected", "path": str(fallback)},
        )

    def test_exact_sync_root_refuses_fallback_without_private_runtime(self):
        self.fake_python(self.sync)
        self.assertEqual(self.select(self.sync), {"status": "refused", "path": ""})
