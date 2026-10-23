"""Fixed local preparation only: no permit issue, decoder or execute command.

The private operator's synthetic-owner session bootstrap is rehearsed separately.
It is not password authentication or permission for a real advertiser identity.
"""

import contextlib
import hashlib
import io
import json
import os
import secrets
import socket
import stat
import sys
import types
from pathlib import Path
from time import monotonic
from unittest.mock import patch

SCHEMA_HELPER_SHA = "d5742e54d168e7e31d64e8ff2ecb68083f7747be0d7c25192d68efabbc69acee"
TARGET = ("connections", "0007_candidate_inspection_permit")
NEW_TABLE = "connections_candidateinspectionpermit"
_LEGACY_REPOSITORY = Path(r"C:\Users\Public\Desktop\GrowthTwin")
_MIGRATION_RELATIVE = Path(
    "apps/web/growthtwin/modules/connections/migrations/0007_candidate_inspection_permit.py"
)


def _bind_repository(helper):
    """Rebind only reviewed repository locations after pinned source loading.

    Database, backup, audit and source-hash bindings remain untouched. This admits
    the single known legacy checkout, never an arbitrary caller-selected root.
    The read-only plan still checks the relocated migration against its manifest.
    """
    current = Path(__file__).resolve().parents[3]
    original = getattr(helper, "REPO", None)
    if (
        original not in (current, _LEGACY_REPOSITORY)
        or getattr(helper, "MIGRATION", None) != original / _MIGRATION_RELATIVE
    ):
        raise ValueError("Repository scope changed.")
    helper.REPO = current
    helper.MIGRATION = current / _MIGRATION_RELATIVE
    return helper


def _load_preparation():
    path = Path(os.environ["TEMP"]) / "gwt_prepare_inspection_schema.py"
    for item in (path, *path.parents):
        info = item.stat(follow_symlinks=False)
        if info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError("Preparation source unavailable.")
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError("Preparation source unavailable.")
    with path.open("rb") as source:
        raw = source.read(65537)
    if len(raw) > 65536 or hashlib.sha256(raw).hexdigest() != SCHEMA_HELPER_SHA:
        raise ValueError("Preparation source changed.")
    module = types.ModuleType("reviewed_schema_preparation")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return _bind_repository(module)


def _owned_synthetic_session(*, owner, workspace_id):
    """Explicit local operator bootstrap; the read-only plan never calls it."""
    from django.conf import settings
    from django.contrib.auth import get_user
    from django.contrib.sessions.backends.db import SessionStore
    from django.contrib.sessions.models import Session
    from django.db import connection
    from django.http import HttpRequest
    from django.utils import timezone
    from django.views.decorators.debug import sensitive_variables

    from growthtwin.modules.workspaces.models import Workspace

    class OwnedSession:
        def __init__(self):
            self._key = None
            self._store = None
            self._expected_data = None
            self._expected_encoded = None
            self._expected_expiry = None
            self._started_at = None
            self._started_monotonic = None
            self._nonce = secrets.token_urlsafe(24)
            self._password = owner.password

        @sensitive_variables()
        def __enter__(self):
            backend = "django.contrib.auth.backends.ModelBackend"
            if (
                connection.in_atomic_block
                or settings.DEBUG is not False
                or not owner.is_active
                or owner.has_usable_password()
                or (str(owner.pk), str(workspace_id))
                != (
                    str(settings.GOOGLE_ADS_LOCAL_OWNER_ID),
                    str(settings.GOOGLE_ADS_LOCAL_WORKSPACE_ID),
                )
                or backend not in settings.AUTHENTICATION_BACKENDS
                or not Workspace.objects.filter(pk=workspace_id, owner=owner).exists()
                or Session.objects.exists()
            ):
                raise ValueError("Synthetic session admission refused.")
            try:
                self._started_at = timezone.now()
                self._started_monotonic = monotonic()
                binding = self

                class MintedSessionStore(SessionStore):
                    @property
                    def key_salt(self):
                        # Preserve the standard backend's signing domain on reload.
                        return SessionStore().key_salt

                    @sensitive_variables()
                    def create_model_instance(self, data):
                        row = super().create_model_instance(data)
                        binding._expected_expiry = row.expire_date
                        return row

                    @sensitive_variables()
                    def encode(self, session_dict):
                        if session_dict != binding._expected_data:
                            raise ValueError("Synthetic session payload changed.")
                        encoded = super().encode(session_dict)
                        binding._expected_encoded = encoded
                        return encoded

                store = self._store = MintedSessionStore()
                store["_auth_user_id"] = str(owner.pk)
                store["_auth_user_backend"] = backend
                store["_auth_user_hash"] = owner.get_session_auth_hash()
                store["inspection_nonce"] = self._nonce
                store.set_expiry(300)
                self._expected_data = dict(store.items())
                store.create()
                self._key = store.session_key
                request = HttpRequest()
                request.session = SessionStore(session_key=self._key)
                authenticated = get_user(request)
                if (
                    not authenticated.is_authenticated
                    or not authenticated.is_active
                    or authenticated.pk != owner.pk
                    or request.session.session_key != self._key
                    or type(request.session.get("inspection_nonce")) is not str
                    or not secrets.compare_digest(
                        request.session["inspection_nonce"], self._nonce
                    )
                    or dict(request.session.items()) != self._expected_data
                    or not Session.objects.filter(
                        session_key=self._key,
                        session_data=self._expected_encoded,
                    ).exists()
                ):
                    raise ValueError("Synthetic session verification refused.")
                self.validate()
                return authenticated, self._key
            except Exception:
                self._cleanup()
                raise

        @sensitive_variables()
        def validate(self):
            now = timezone.now()
            observed_monotonic = monotonic()
            if (
                self._key is None
                or self._expected_expiry is None
                or self._started_at is None
                or self._started_monotonic is None
                or not self._started_at <= now < self._expected_expiry
                or not self._started_monotonic
                <= observed_monotonic
                < self._started_monotonic + 300
                or not Session.objects.filter(
                    session_key=self._key,
                    session_data=self._expected_encoded,
                    expire_date=self._expected_expiry,
                    expire_date__gt=now,
                ).exists()
                or not type(owner)
                .objects.filter(pk=owner.pk, is_active=True, password=self._password)
                .exists()
                or not Workspace.objects.filter(pk=workspace_id, owner=owner).exists()
            ):
                raise ValueError("Synthetic session deadline or binding changed.")
            finished_at = timezone.now()
            finished_monotonic = monotonic()
            if (
                not self._started_at <= finished_at < self._expected_expiry
                or not self._started_monotonic
                <= finished_monotonic
                < self._started_monotonic + 300
            ):
                raise ValueError("Synthetic session deadline or binding changed.")

        @sensitive_variables()
        def _cleanup(self):
            key = self._key or (
                self._store.session_key if self._store is not None else None
            )
            if key is not None:
                row = Session.objects.filter(session_key=key).first()
                if row is not None:
                    data = row.get_decoded()
                    nonce = data.get("inspection_nonce")
                    if (
                        row.session_data != self._expected_encoded
                        or row.expire_date != self._expected_expiry
                        or data != self._expected_data
                        or type(nonce) is not str
                        or not secrets.compare_digest(nonce, self._nonce)
                        or data.get("_auth_user_id") != str(owner.pk)
                    ):
                        raise ValueError("Synthetic session cleanup requires review.")
                    Session.objects.filter(
                        session_key=key,
                        session_data=self._expected_encoded,
                        expire_date=self._expected_expiry,
                    ).delete()
            current = type(owner).objects.get(pk=owner.pk)
            if current.password != self._password or Session.objects.exists():
                raise ValueError("Synthetic session cleanup requires review.")

        @sensitive_variables()
        def __exit__(self, *_):
            self._cleanup()
            return False

    return OwnedSession()


def _plan():
    helper = _load_preparation()
    audit = helper.load_audit()
    helper.admission(audit, migrated=True)
    pointer = helper.read_json(audit, helper.POINTER)
    parent = Path(os.environ["LOCALAPPDATA"]) / "Temp"
    root = Path(pointer["backup_root"])
    if (
        type(pointer.get("version")) is not int
        or pointer["version"] != 1
        or not root.is_absolute()
        or root.parent != parent
        or not root.name.startswith("gwt-inspection-schema-backup-")
    ):
        raise ValueError("Backup scope changed.")
    backup, manifest_path = root / "before-0007.sqlite3", root / "manifest.json"
    for path in (
        root,
        backup,
        manifest_path,
        helper.MIGRATION,
        helper.AUDIT,
        helper.ROOT / "preparation.json",
    ):
        audit.no_reparse(path)
    if not audit.private_acls([root, backup, manifest_path]):
        raise ValueError("Backup access changed.")
    manifest = helper.read_json(audit, manifest_path)
    if (
        type(manifest.get("version")) is not int
        or manifest["version"] != 1
        or manifest["plan"] != [[*TARGET, False]]
        or helper.hash_file(backup) != manifest["backup_hash"]
        or helper.hash_file(helper.AUDIT) != manifest["audit_hash"]
        or helper.hash_file(helper.MIGRATION) != manifest["migration_hash"]
        or helper.hash_file(helper.ROOT / "preparation.json")
        != manifest["preparation_hash"]
        or helper.hash_value(helper.snapshot(audit, backup))
        != helper.hash_value(manifest["before"])
    ):
        raise ValueError("Preparation evidence changed.")
    before_hash = helper.hash_file(helper.DB)
    after = helper.snapshot(audit, helper.DB, exclude_new=True)
    before = manifest["before"]
    old_schema = {row[1]: tuple(row) for row in before["schema"]}
    new_schema = {row[1]: tuple(row) for row in after["schema"]}
    added = [row for name, row in new_schema.items() if name not in old_schema]
    if (
        any(new_schema.get(name) != row for name, row in old_schema.items())
        or not added
        or any(row[2] != NEW_TABLE or row[0] not in ("table", "index") for row in added)
        or after["data"] != before["data"]
        or after["permit_count"] != 0
        or sorted(map(tuple, after["migrations"]))
        != sorted([*map(tuple, before["migrations"]), TARGET])
        or helper.hash_file(helper.DB) != before_hash
    ):
        raise ValueError("Post-schema scope changed.")
    return {
        "read_only_admission": True,
        "same_candidate_history_preserved": True,
        "verified_private_backup": True,
        "permit_count": 0,
        "session_count": 0,
        "credential_contents_read": False,
        "current_client_hash_proved": False,
        "execution_available": False,
    }


def main():
    if os.name != "nt" or sys.argv[1:] != ["plan"]:
        raise ValueError("Only the Windows read-only plan command exists.")
    captured = io.StringIO()
    with (
        patch.object(socket, "create_connection", side_effect=AssertionError) as one,
        patch.object(socket.socket, "connect", side_effect=AssertionError) as two,
        contextlib.redirect_stdout(captured),
    ):
        result = _plan()
    if one.call_count or two.call_count or captured.getvalue():
        raise ValueError("Unexpected preparation boundary.")
    print(json.dumps(result))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print('{"preparation_refused":true,"details_suppressed":true}')
        raise SystemExit(1) from None
