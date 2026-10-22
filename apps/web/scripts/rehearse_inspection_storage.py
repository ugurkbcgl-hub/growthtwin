"""Windows-only real DPAPI rehearsal using disposable fabricated files only.

Run from apps/web with the project Python. No saved configuration, database,
provider, existing credential or caller-supplied path is used. Prints counts only.
"""

import json
import os
import secrets
import socket
import sys
import tempfile
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch


def main():
    if os.name != "nt":
        print("Windows is required; rehearsal not run.")
        return 2
    # Do not reuse a saved application secret or database configuration.
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.test_settings"
    os.environ["DJANGO_SECRET_KEY"] = secrets.token_urlsafe(48)
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import django
    from django.db.backends.base.base import BaseDatabaseWrapper

    with ExitStack() as startup:
        forbidden = [
            startup.enter_context(
                patch.object(
                    BaseDatabaseWrapper,
                    "ensure_connection",
                    side_effect=AssertionError("Database access forbidden"),
                )
            ),
            startup.enter_context(
                patch.object(
                    socket,
                    "create_connection",
                    side_effect=AssertionError("Network access forbidden"),
                )
            ),
            startup.enter_context(
                patch.object(
                    socket.socket,
                    "connect",
                    side_effect=AssertionError("Network access forbidden"),
                )
            ),
        ]
        try:
            django.setup()
            return _run(forbidden)
        except Exception:
            print(
                json.dumps(
                    {
                        "passed": False,
                        "setup_failed": True,
                        "forbidden_boundary_attempts": sum(
                            item.call_count for item in forbidden
                        ),
                    }
                )
            )
            return 1


def _run(forbidden):
    from django.test import override_settings

    from growthtwin.modules.connections import backend
    from growthtwin.modules.connections import candidate_inspection_storage as storage

    # Encrypt raw *fabricated* JSON for decoder errors, preserving CreateNew.
    encrypt_raw = r"""
    $ErrorActionPreference='Stop'
    try {
      $d=[Console]::In.ReadToEnd() | ConvertFrom-Json
      $secure=ConvertTo-SecureString -String $d.text -AsPlainText -Force
      try {
        $cipher=ConvertFrom-SecureString $secure
        $bytes=[Text.Encoding]::UTF8.GetBytes($cipher)
        $stream=[IO.File]::Open($d.path,[IO.FileMode]::CreateNew)
        try {$stream.Write($bytes,0,$bytes.Length)} finally {$stream.Dispose()}
      } finally {$secure.Dispose()}
    } catch {exit 1}
    """
    root = None
    owned = []
    checks = 0
    cleanup_ok = False
    plain_limit_isolated = False
    passed = False
    try:
        parent = Path(os.environ["LOCALAPPDATA"]) / "Temp"
        if not parent.is_absolute() or ".." in parent.parts or not parent.is_dir():
            raise ValueError
        root = Path(tempfile.mkdtemp(prefix="gwt-dpapi-rehearsal-", dir=parent))
        original_root = root.resolve(strict=True)
        if root.parent.resolve(strict=True) != parent.resolve(strict=True):
            raise ValueError
        if original_root != root:
            raise ValueError

        def exact(name):
            path = root / name
            if path.parent != root or path.name != name or path in owned:
                raise ValueError
            owned.append(path)
            return path

        def reject(path):
            nonlocal checks
            try:
                storage._read_bounded(path)
            except backend.ConnectionUnavailable as error:
                if str(error) != "Inspection storage is unavailable.":
                    raise AssertionError from None
            else:
                raise AssertionError("Fabricated invalid input was accepted.")
            checks += 1

        with ExitStack() as stack:
            stack.enter_context(
                override_settings(GOOGLE_ADS_LOCAL_OAUTH_ENABLED=True, DEBUG=False)
            )
            for name in ("_client", "_read", "_post", "_token_path"):
                forbidden.append(
                    stack.enter_context(
                        patch.object(
                            backend,
                            name,
                            side_effect=AssertionError("Forbidden boundary"),
                        )
                    )
                )
            path = exact("valid.dpapi")
            expected = {"example": "İstanbul — ü, ş, ğ", "payload": "x" * 1024}
            # Existing writer sets the fresh directory to current-user-only ACL.
            backend._write(path, expected)
            if storage._read_bounded(path) != expected:
                raise AssertionError
            checks += 1

            path = exact("large-valid.dpapi")
            expected = {"payload": "x" * 30000}
            backend._write(path, expected)
            if storage._read_bounded(path) != expected:
                raise AssertionError
            checks += 1

            for name, text in (
                ("duplicate.dpapi", '{"key":1,"key":2}'),
                ("malformed.dpapi", "{broken-json}"),
                ("nonobject.dpapi", "[1,2,3]"),
                ("constant.dpapi", '{"key":NaN}'),
            ):
                path = exact(name)
                backend._powershell(encrypt_raw, {"path": str(path), "text": text})
                reject(path)

            for name, data in (
                ("empty.dpapi", b""),
                ("invalid-utf8.dpapi", b"\xff\xfe\xff"),
                ("bad-cipher.dpapi", b"fabricated-not-dpapi"),
                ("over-encrypted.dpapi", b"x" * (storage.MAX_ENCRYPTED_BYTES + 1)),
            ):
                path = exact(name)
                with path.open("xb") as output:
                    output.write(data)
                reject(path)
            reject(exact("missing.dpapi"))

            path = exact("over-plaintext.dpapi")
            text = json.dumps({"payload": "x" * storage.MAX_PLAINTEXT_CHARS})
            backend._powershell(encrypt_raw, {"path": str(path), "text": text})
            # DPAPI ciphertext expansion can hit the encrypted cap first. Do not
            # claim that this independently exercised the later plaintext guard.
            plain_limit_isolated = path.stat().st_size <= storage.MAX_ENCRYPTED_BYTES
            reject(path)
            passed = not any(boundary.call_count for boundary in forbidden)
    except Exception:
        # Never print tracebacks, plaintext, ciphertext, paths or exception bodies.
        passed = False
    finally:
        if root is not None:
            try:
                if root.resolve(strict=True) != original_root:
                    raise ValueError
                for path in owned:
                    if path.parent != original_root:
                        raise ValueError
                    path.unlink(missing_ok=True)
                root.rmdir()  # Nonrecursive: unexpected files stop cleanup.
                cleanup_ok = True
            except Exception:
                cleanup_ok = False
    print(
        json.dumps(
            {
                "passed": passed and cleanup_ok,
                "checks_passed": checks,
                "cleanup_complete": cleanup_ok,
                "plaintext_limit_independently_exercised": plain_limit_isolated,
                "database_or_provider_access": False,
                "forbidden_boundary_attempts": sum(
                    item.call_count for item in forbidden
                ),
            }
        )
    )
    return 0 if passed and cleanup_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
