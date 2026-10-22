"""Opt-in local Windows OAuth transport and user-scoped encrypted storage.

Only fixed Google token/revocation endpoints are used. No Ads API is called.
Subprocess input/output stays captured; errors never include provider bodies.
"""

import hashlib
import json
import os
import subprocess
import threading
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from django.conf import settings
from django.views.decorators.debug import sensitive_variables

from .google_oauth import ADS_SCOPE, LOCAL_REDIRECT_URI

_LOCK = threading.Lock()


class ConnectionUnavailable(Exception):
    def __init__(self, message="Connection unavailable.", *, reason="unavailable"):
        super().__init__(message)
        self.reason = (
            reason
            if reason
            in {
                "unavailable",
                "network",
                "google_rejected",
                "invalid_client",
                "invalid_grant",
                "token_shape",
                "storage",
            }
            else "unavailable"
        )


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _enabled():
    if (
        not getattr(settings, "GOOGLE_ADS_LOCAL_OAUTH_ENABLED", False)
        or settings.DEBUG
        or os.name != "nt"
    ):
        raise ConnectionUnavailable("Local connection is unavailable.")


@sensitive_variables()
def _token_path(binding):
    # Session binds the handshake, not the durable owner/workspace credential.
    if (
        not isinstance(binding, tuple)
        or len(binding) != 3
        or not all(isinstance(value, str) and value for value in binding)
        or binding[:2]
        != (
            str(settings.GOOGLE_ADS_LOCAL_OWNER_ID),
            str(settings.GOOGLE_ADS_LOCAL_WORKSPACE_ID),
        )
    ):
        raise ConnectionUnavailable("Local connection is unavailable.")
    identity = hashlib.sha256(json.dumps(binding[:2]).encode()).hexdigest()
    return (
        Path(os.environ["LOCALAPPDATA"])
        / "GrowthTwinsecrets"
        / f"google-{identity}.dpapi"
    )


@sensitive_variables()
def _powershell(script, payload):
    _enabled()
    # PowerShell 7 callers can supply a module search path that omits Windows
    # PowerShell built-ins; import the inbox security module explicitly.
    script = (
        "$env:PATHEXT='.COM;.EXE;.BAT;.CMD'\n"
        "Import-Module (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Security/Microsoft.PowerShell.Security.psd1') -ErrorAction Stop\n"
        + script
    )
    executable = (
        Path(os.environ["SystemRoot"])
        / "System32/WindowsPowerShell/v1.0/powershell.exe"
    )
    try:
        result = subprocess.run(
            [
                str(executable),
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                script,
            ],
            input=json.dumps(payload),
            text=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if result.returncode:
            raise ValueError
        return result.stdout
    except Exception:
        raise ConnectionUnavailable(
            "Encrypted credential storage is unavailable."
        ) from None


@sensitive_variables()
def _read(path):
    script = """
    $ErrorActionPreference='Stop'
    try {
      $inputData=[Console]::In.ReadToEnd() | ConvertFrom-Json
      $s=ConvertTo-SecureString ([IO.File]::ReadAllText($inputData.path))
      $ptr=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($s)
      try { [Console]::Out.Write([Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)) }
      finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
    } catch {exit 1}
    """
    try:
        return json.loads(_powershell(script, {"path": str(path)}))
    except Exception:
        raise ConnectionUnavailable(
            "Encrypted credential storage is unavailable."
        ) from None


@sensitive_variables()
def _write(path, data):
    # No plaintext file, command-line secret, or inherited public-directory ACL.
    script = """
    $ErrorActionPreference='Stop'
    try {
      $d=[Console]::In.ReadToEnd() | ConvertFrom-Json
      $dir=[IO.Path]::GetDirectoryName($d.path)
      [void][IO.Directory]::CreateDirectory($dir)
      $sid=[Security.Principal.WindowsIdentity]::GetCurrent().User
      & "$env:SystemRoot/System32/icacls.exe" $dir /inheritance:r /grant:r (
        '*'+$sid.Value+':(OI)(CI)F') | Out-Null
      if($LASTEXITCODE -ne 0){throw 'ACL failed'}
      $s=ConvertTo-SecureString -String $d.data -AsPlainText -Force
      $encrypted=ConvertFrom-SecureString $s
      $stream=[IO.File]::Open($d.path,[IO.FileMode]::CreateNew)
      try {
        $bytes=[Text.Encoding]::UTF8.GetBytes($encrypted)
        $stream.Write($bytes,0,$bytes.Length)
      } finally {$stream.Dispose()}
    } catch {exit 1}
    """
    _powershell(script, {"path": str(path), "data": json.dumps(data)})


@sensitive_variables()
def _client():
    _enabled()
    path = (
        Path(os.environ["LOCALAPPDATA"])
        / "GrowthTwinsecrets/google-ads-oauth-client.dpapi"
    )
    value = _read(path)
    if (
        not isinstance(value, dict)
        or value.get("project_id") != "growthtwin-ads-test"
        or value.get("type") != "web"
        or not isinstance(value.get("client_id"), str)
        or not value["client_id"].endswith(".apps.googleusercontent.com")
        or not isinstance(value.get("client_secret"), str)
        or not value["client_secret"]
    ):
        raise ConnectionUnavailable("Invalid local client configuration.")
    return value


def load_client_id():
    return _client()["client_id"]


@sensitive_variables()
def _post(endpoint, fields):
    try:
        if endpoint not in {
            "https://oauth2.googleapis.com/token",
            "https://oauth2.googleapis.com/revoke",
        }:
            raise ValueError
        request = Request(
            endpoint,
            data=urlencode(fields).encode("ascii"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with build_opener(_NoRedirect()).open(request, timeout=20) as response:
            body = response.read(65537)
            if len(body) > 65536 or response.status != 200:
                raise ValueError
            return body
    except HTTPError as error:
        reason = "google_rejected"
        try:
            payload = json.loads(error.read(4096))
            if isinstance(payload, dict) and payload.get("error") in {
                "invalid_client",
                "invalid_grant",
            }:
                reason = payload["error"]
        except Exception:
            pass
        finally:
            error.close()
        raise ConnectionUnavailable(
            "Google rejected authorization.", reason=reason
        ) from None
    except (URLError, TimeoutError):
        raise ConnectionUnavailable(
            "Google could not be reached.", reason="network"
        ) from None
    except Exception:
        raise ConnectionUnavailable(
            "Google authorization could not be completed."
        ) from None


def connection_exists(binding):
    _enabled()
    return _token_path(binding).is_file()


@sensitive_variables()
def exchange_and_store(authorization_code, binding):
    _enabled()
    with _LOCK:
        path = _token_path(binding)
        if path.exists():
            raise ConnectionUnavailable(
                "Disconnect before starting another authorization."
            )
        client = _client()
        token = None
        stage = "token_shape"
        try:
            token = json.loads(
                _post(
                    "https://oauth2.googleapis.com/token",
                    {
                        "client_id": client["client_id"],
                        "client_secret": client["client_secret"],
                        "code": authorization_code.code,
                        "code_verifier": authorization_code.verifier,
                        "redirect_uri": LOCAL_REDIRECT_URI,
                        "grant_type": "authorization_code",
                    },
                )
            )
            if (
                not isinstance(token, dict)
                or token.get("token_type", "").lower() != "bearer"
                or not isinstance(token.get("refresh_token"), str)
                or not token["refresh_token"]
                or not isinstance(token.get("access_token"), str)
                or not token["access_token"]
                or set(token.get("scope", "").split()) != {ADS_SCOPE}
            ):
                raise ValueError
            stage = "storage"
            _write(path, {"refresh_token": token["refresh_token"], "scope": ADS_SCOPE})
        except Exception as error:
            reason = (
                error.reason
                if isinstance(error, ConnectionUnavailable) and stage != "storage"
                else stage
            )
            if isinstance(token, dict) and isinstance(token.get("access_token"), str):
                try:
                    _post(
                        "https://oauth2.googleapis.com/revoke",
                        {"token": token["access_token"]},
                    )
                except ConnectionUnavailable:
                    pass
            raise ConnectionUnavailable(
                "Authorization was not saved. Check Google account permissions before retrying.",
                reason=reason,
            ) from None


@sensitive_variables()
def disconnect(binding):
    _enabled()
    with _LOCK:
        path = _token_path(binding)
        if not path.exists():
            return
        token = _read(path)
        _post("https://oauth2.googleapis.com/revoke", {"token": token["refresh_token"]})
        path.unlink()
