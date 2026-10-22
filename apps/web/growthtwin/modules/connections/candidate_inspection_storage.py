"""Private bounded storage boundary for the closed recovered-inspection reader.

No provider or writes. All tests replace filesystem and PowerShell operations.
Reparse checks are best effort, not a production no-follow/vault guarantee.
"""

import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.views.decorators.debug import sensitive_variables

from . import backend
from . import scoped_oauth_candidate as candidate

MAX_ENCRYPTED_BYTES = 131072
MAX_PLAINTEXT_CHARS = 32768

# Fixed bounds are internal; no caller can increase them. FileShare.Read excludes
# simultaneous write/delete opens while our handle is held. Ancestor/reparse
# checks cannot establish an atomic no-follow guarantee against a privileged actor.
_BOUNDED_READ_SCRIPT = r"""
$ErrorActionPreference='Stop'
try {
  $inputData=[Console]::In.ReadToEnd() | ConvertFrom-Json
  $path=[IO.Path]::GetFullPath($inputData.path)
  $current=$path
  while($current) {
    $attributes=[IO.File]::GetAttributes($current)
    if(($attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'Invalid storage'}
    $current=[IO.Path]::GetDirectoryName($current)
  }
  $attributes=[IO.File]::GetAttributes($path)
  if(($attributes -band [IO.FileAttributes]::Directory) -ne 0){throw 'Invalid storage'}
  $stream=[IO.File]::Open($path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read)
  try {
    if($stream.Length -le 0 -or $stream.Length -gt 131072){throw 'Invalid storage'}
    $buffer=New-Object byte[] 131073
    $count=0
    while($count -lt $buffer.Length) {
      $read=$stream.Read($buffer,$count,$buffer.Length-$count)
      if($read -eq 0){break}
      $count+=$read
    }
    if($count -le 0 -or $count -gt 131072){throw 'Invalid storage'}
    $utf8=[Text.UTF8Encoding]::new($false,$true)
    $encrypted=$utf8.GetString($buffer,0,$count)
    $secure=ConvertTo-SecureString $encrypted
    try {
      if($secure.Length -le 0 -or $secure.Length -gt 32768){throw 'Invalid storage'}
      $ptr=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
      try {
        $plain=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
        if($plain.Length -le 0 -or $plain.Length -gt 32768){throw 'Invalid storage'}
        [Console]::Out.Write($plain)
      } finally {[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)}
    } finally {$secure.Dispose()}
  } finally {$stream.Dispose()}
} catch {exit 1}
"""


@dataclass(frozen=True, repr=False)
class StorageLocations:
    root: Path
    client: Path
    legacy: Path
    candidate: Path


def _unavailable():
    return backend.ConnectionUnavailable("Inspection storage is unavailable.")


@sensitive_variables()
def _locations(*, owner_id, workspace_id, session_key, receipt):
    try:
        pair = (str(owner_id), str(workspace_id))
        if pair != (
            str(settings.GOOGLE_ADS_LOCAL_OWNER_ID),
            str(settings.GOOGLE_ADS_LOCAL_WORKSPACE_ID),
        ) or any(not value or value == "None" for value in pair):
            raise ValueError
        candidate._session_key(session_key)
        appdata = Path(os.environ["LOCALAPPDATA"])
        if (
            not appdata.is_absolute()
            or ".." in appdata.parts
            or str(appdata).startswith(("\\\\", "//"))
            or len(str(appdata)) > 32000
        ):
            raise ValueError
        root = appdata / "GrowthTwinsecrets"
        client = root / "google-ads-oauth-client.dpapi"
        legacy = backend._token_path((*pair, session_key))
        candidate_path = candidate._candidate_path(receipt)
        if (
            any(
                type(path) is not type(root)
                for path in (client, legacy, candidate_path)
            )
            or any(path.parent != root for path in (client, legacy, candidate_path))
            or len({client, legacy, candidate_path}) != 3
        ):
            raise ValueError
        return StorageLocations(root, client, legacy, candidate_path)
    except Exception:
        raise _unavailable() from None


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate JSON key.")
        value[key] = item
    return value


def _constant(value):
    raise ValueError("Non-JSON constant.")


@sensitive_variables()
def _read_bounded(path):
    try:
        if not isinstance(path, Path) or not path.is_absolute():
            raise ValueError
        result = backend._powershell(_BOUNDED_READ_SCRIPT, {"path": str(path)})
        if type(result) is not str or not 1 <= len(result) <= MAX_PLAINTEXT_CHARS:
            raise ValueError
        # The existing process helper decodes strict UTF-8 before returning text.
        value = json.loads(
            result, object_pairs_hook=_unique_object, parse_constant=_constant
        )
        if type(value) is not dict:
            raise ValueError
        return value
    except Exception:
        raise _unavailable() from None


@sensitive_variables()
def _client_key(locations):
    try:
        value = _read_bounded(locations.client)
        if (
            value.get("project_id") != "growthtwin-ads-test"
            or value.get("type") != "web"
            or type(value.get("client_secret")) is not str
            or not 1 <= len(value["client_secret"]) <= 8192
        ):
            raise ValueError
        return candidate._client_key(value.get("client_id"))
    except Exception:
        raise _unavailable() from None


@sensitive_variables()
def _legacy_present(locations):
    try:
        info = locations.legacy.stat(follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode) or (
            getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
        ):
            raise ValueError
        return True
    except FileNotFoundError:
        return False
    except Exception:
        raise _unavailable() from None
