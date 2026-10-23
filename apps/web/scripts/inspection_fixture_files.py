"""Private disposable Windows fixture files. Importing performs no operations.

Only fresh roots registered by this module are eligible for mutation. The checks
are best effort against path races, not atomic no-follow or a production vault.
"""

import json
import os
import stat
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from django.views.decorators.debug import sensitive_variables

_ORIGINAL_APPDATA = os.environ.get("LOCALAPPDATA")
_PREFIX = "gwt-inspection-once-fixture-"


@dataclass(repr=False)
class _Home:
    parent: Path
    identity: tuple
    directories: dict = field(default_factory=dict)


_HOMES = {}

_ACL_CHECK = r"""
$acl=Get-Acl -LiteralPath $d.path -ErrorAction Stop
if([IO.Directory]::Exists($d.path) -and -not $acl.AreAccessRulesProtected){throw 'Refused'}
$sid=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value
if($acl.GetOwner([Security.Principal.SecurityIdentifier]).Value -ne $sid){throw 'Refused'}
$rules=@($acl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier]))
if($rules.Count -eq 0){throw 'Refused'}
foreach($rule in $rules){
  if($rule.IdentityReference.Value -ne $sid -or $rule.AccessControlType -ne 'Allow' -or
     ($rule.FileSystemRights -band [Security.AccessControl.FileSystemRights]::FullControl) -ne
       [Security.AccessControl.FileSystemRights]::FullControl){throw 'Refused'}
}
"""

_SECURE = (
    r"""
if(-not [IO.Directory]::Exists($d.path) -or [IO.Directory]::GetFileSystemEntries($d.path).Length -ne 0){throw 'Refused'}
$acl=Get-Acl -LiteralPath $d.path -ErrorAction Stop
$sid=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value
if($acl.GetOwner([Security.Principal.SecurityIdentifier]).Value -ne $sid){throw 'Refused'}
& "$env:SystemRoot/System32/icacls.exe" $d.path /reset | Out-Null
if($LASTEXITCODE){throw 'Refused'}
& "$env:SystemRoot/System32/icacls.exe" $d.path /inheritance:r /grant:r ('*'+$sid+':(OI)(CI)F') | Out-Null
if($LASTEXITCODE){throw 'Refused'}
"""
    + _ACL_CHECK
    + r"""
if(-not $acl.AreAccessRulesProtected){throw 'Refused'}
"""
)

_ENCRYPT = r"""
if([IO.File]::Exists($d.path) -or [IO.Directory]::Exists($d.path)){throw 'Refused'}
$secure=ConvertTo-SecureString -String $d.text -AsPlainText -Force
try {
  $cipher=ConvertFrom-SecureString $secure
  $bytes=[Text.Encoding]::UTF8.GetBytes($cipher)
  $stream=[IO.File]::Open($d.path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
  try {$stream.Write($bytes,0,$bytes.Length)} finally {$stream.Dispose()}
} finally {$secure.Dispose()}
"""


def _windows():
    if os.name != "nt":
        raise ValueError("Windows fixture files are unavailable.")


def _shape(path):
    if (
        not isinstance(path, Path)
        or not path.is_absolute()
        or ".." in path.parts
        or str(path).startswith(("\\\\", "//"))
        or len(str(path)) > 32000
    ):
        raise ValueError("Fixture path refused.")


def no_reparse(path):
    _shape(path)
    for item in (path, *path.parents):
        info = item.stat(follow_symlinks=False)
        if stat.S_ISLNK(info.st_mode) or (
            getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
        ):
            raise ValueError("Fixture path refused.")


def _identity(path):
    info = path.stat(follow_symlinks=False)
    return info.st_dev, info.st_ino


def _owned(path):
    _shape(path)
    for home, record in _HOMES.items():
        if path == home or home in path.parents:
            no_reparse(home)
            if (
                home.parent != record.parent
                or home.resolve(strict=True) != home
                or _identity(home) != record.identity
            ):
                raise ValueError("Fixture root changed.")
            for directory in (path, *path.parents):
                if directory in record.directories:
                    no_reparse(directory)
                    if _identity(directory) != record.directories[directory]:
                        raise ValueError("Fixture directory changed.")
            return home, record
    raise ValueError("Unknown fixture root.")


@sensitive_variables()
def _native(script, payload):
    _windows()
    executable = (
        Path(os.environ["SystemRoot"])
        / "System32/WindowsPowerShell/v1.0/powershell.exe"
    )
    wrapped = (
        r"""
$ErrorActionPreference='Stop'
try {
  Import-Module (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Security/Microsoft.PowerShell.Security.psd1') -ErrorAction Stop
  $d=[Console]::In.ReadToEnd() | ConvertFrom-Json
"""
        + script
        + r"""
  [Console]::Out.Write('{"ok":true}')
} catch {exit 1}
"""
    )
    try:
        result = subprocess.run(
            [
                str(executable),
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                wrapped,
            ],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            check=False,
        )
        if result.returncode or result.stdout != '{"ok":true}':
            raise ValueError
    except Exception:
        raise ValueError("Fixture native operation refused.") from None


def assert_private(path):
    _owned(path)
    no_reparse(path)
    info = path.stat(follow_symlinks=False)
    if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
        raise ValueError("Fixture object refused.")
    _native(_ACL_CHECK, {"path": str(path)})


def _secure_new(path):
    _owned(path)
    no_reparse(path)
    if not path.is_dir() or any(path.iterdir()):
        raise ValueError("Only an empty fixture directory is eligible.")
    _native(_SECURE, {"path": str(path)})
    assert_private(path)


def create_home():
    _windows()
    if not _ORIGINAL_APPDATA:
        raise ValueError("Fixture parent unavailable.")
    parent = Path(_ORIGINAL_APPDATA) / "Temp"
    no_reparse(parent)
    if not parent.is_dir() or parent.resolve(strict=True) != parent:
        raise ValueError("Fixture parent unavailable.")
    home = Path(tempfile.mkdtemp(prefix=_PREFIX, dir=parent))
    _HOMES[home] = _Home(parent, _identity(home), {home: _identity(home)})
    _secure_new(home)
    return home


def make_private_directory(path):
    home, record = _owned(path)
    if (
        path == home
        or path in record.directories
        or path.parent not in record.directories
    ):
        raise ValueError("Only a new direct fixture descendant is eligible.")
    assert_private(path.parent)
    path.mkdir()  # Existing paths, including dangling links, are refused.
    record.directories[path] = _identity(path)
    _secure_new(path)
    return path


@sensitive_variables()
def encrypt_new(path, value):
    _, record = _owned(path)
    if path.parent not in record.directories or type(value) is not dict:
        raise ValueError("Fixture encryption refused.")
    assert_private(path.parent)
    if path.exists() or path.is_symlink():
        raise ValueError("Fixture output already exists.")
    text = json.dumps(value, allow_nan=False, ensure_ascii=False)
    if not 1 <= len(text) <= 32768:
        raise ValueError("Fixture payload refused.")
    _native(_ENCRYPT, {"path": str(path), "text": text})
    assert_private(path)


def cleanup(home, files, directories):
    actual_home, record = _owned(home)
    if actual_home != home:
        raise ValueError("Cleanup requires the exact fixture root.")
    files, directories = list(files), list(directories)
    if len(set(files)) != len(files) or len(set(directories)) != len(directories):
        raise ValueError("Duplicate cleanup entries refused.")
    for path in files:
        found_home, _ = _owned(path)
        if found_home != home or path == home or path.parent not in record.directories:
            raise ValueError("Cleanup scope refused.")
        if path.exists() or path.is_symlink():
            if path.name.endswith(("-journal", "-wal", "-shm")):
                raise ValueError("Unexpected SQLite companion requires review.")
            assert_private(path)
            if not stat.S_ISREG(path.stat(follow_symlinks=False).st_mode):
                raise ValueError("Cleanup file refused.")
    for path in directories:
        if path == home or path not in record.directories:
            raise ValueError("Cleanup directory refused.")
        assert_private(path)
        if not path.is_dir():
            raise ValueError("Cleanup directory refused.")
    assert_private(home)
    for path in files:
        _owned(path)
        if path.exists() or path.is_symlink():
            assert_private(path)
            path.unlink()
    for path in sorted(directories, key=lambda item: len(item.parts), reverse=True):
        _owned(path)
        assert_private(path)
        path.rmdir()
    _owned(home)
    assert_private(home)
    home.rmdir()  # Unexpected entries prevent success; never recurse.
    del _HOMES[home]
    return True
