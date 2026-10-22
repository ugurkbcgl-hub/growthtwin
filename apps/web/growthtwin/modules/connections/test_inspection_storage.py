"""Storage source contract only; all file/stat/decryption boundaries are mocked."""

import hashlib
import json
import os
import stat
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.test import SimpleTestCase, override_settings

from . import backend
from . import candidate_inspection_storage as storage


@override_settings(GOOGLE_ADS_LOCAL_OWNER_ID=107, GOOGLE_ADS_LOCAL_WORKSPACE_ID=214)
class InspectionStorageTests(SimpleTestCase):
    def setUp(self):
        self.appdata = Path(Path.cwd().anchor) / "fabricated-inspection-only"
        self.receipt = SimpleNamespace(
            connection_id=uuid4(), generation=uuid4(), pk=uuid4()
        )
        environment = patch.dict(os.environ, {"LOCALAPPDATA": str(self.appdata)})
        environment.start()
        self.addCleanup(environment.stop)

    def locations(self, **changes):
        values = dict(
            owner_id=107,
            workspace_id=214,
            session_key="fabricated-current-session",
            receipt=self.receipt,
        )
        return storage._locations(**(values | changes))

    def assert_unavailable(self, call):
        with self.assertRaises(backend.ConnectionUnavailable) as caught:
            call()
        self.assertEqual(str(caught.exception), "Inspection storage is unavailable.")
        self.assertIsNone(caught.exception.__cause__)
        self.assertTrue(caught.exception.__suppress_context__)

    def test_exact_fixed_paths_match_existing_durable_derivation_without_io(self):
        with (
            patch.object(Path, "stat", side_effect=AssertionError("No stat")),
            patch.object(backend, "_powershell", side_effect=AssertionError("No I/O")),
        ):
            locations = self.locations()
        root = self.appdata / "GrowthTwinsecrets"
        identity = hashlib.sha256(json.dumps(("107", "214")).encode()).hexdigest()
        key = hashlib.sha256(
            (
                str(self.receipt.connection_id)
                + ":"
                + str(self.receipt.generation)
                + ":"
                + str(self.receipt.pk)
            ).encode()
        ).hexdigest()
        self.assertEqual(locations.root, root)
        self.assertEqual(locations.client, root / "google-ads-oauth-client.dpapi")
        self.assertEqual(locations.legacy, root / f"google-{identity}.dpapi")
        self.assertEqual(locations.candidate, root / f"google-candidate-{key}.dpapi")

    def test_new_session_preserves_same_durable_legacy_location(self):
        first = self.locations()
        second = self.locations(session_key="different-fabricated-session")
        self.assertEqual(first, second)

    def test_location_is_frozen_and_repr_does_not_disclose_paths(self):
        locations = self.locations()
        self.assertNotIn(str(self.appdata), repr(locations))
        self.assertNotIn("dpapi", repr(locations))
        with self.assertRaises(FrozenInstanceError):
            locations.client = self.appdata / "other"

    def test_wrong_configured_scope_denies_derivation(self):
        for changes in ({"owner_id": 108}, {"workspace_id": 215}):
            self.assert_unavailable(lambda: self.locations(**changes))
        with override_settings(GOOGLE_ADS_LOCAL_OWNER_ID=None):
            self.assert_unavailable(self.locations)

    def test_missing_or_invalid_session_denies_derivation(self):
        for value in (None, "", 1, "x" * 257):
            self.assert_unavailable(lambda: self.locations(session_key=value))

    def test_relative_traversal_network_or_missing_root_denies(self):
        for value in (
            "fabricated-relative",
            str(self.appdata / ".." / "other"),
            "\\\\fabricated-server\\share",
            "//fabricated-server/share",
            "x" * 32001,
        ):
            with patch.dict(os.environ, {"LOCALAPPDATA": value}):
                self.assert_unavailable(self.locations)
        with patch.dict(os.environ):
            os.environ.pop("LOCALAPPDATA", None)
            self.assert_unavailable(self.locations)

    def test_distinct_parent_root_required_for_all_derived_paths(self):
        root = self.appdata / "GrowthTwinsecrets"
        for target, value in (
            ("_token_path", self.appdata / "outside.dpapi"),
            ("_token_path", root / "google-ads-oauth-client.dpapi"),
            ("_token_path", "not-a-path"),
        ):
            with patch.object(backend, target, return_value=value):
                self.assert_unavailable(self.locations)
        with patch.object(
            storage.candidate, "_candidate_path", return_value=self.appdata / "outside"
        ):
            self.assert_unavailable(self.locations)

    def test_rederivation_detects_environment_and_configured_scope_change(self):
        before = self.locations()
        with patch.dict(os.environ, {"LOCALAPPDATA": str(self.appdata / "different")}):
            self.assertNotEqual(self.locations(), before)
        with override_settings(GOOGLE_ADS_LOCAL_WORKSPACE_ID=215):
            self.assert_unavailable(self.locations)

    def test_bounded_decoder_uses_only_private_fixed_script_and_exact_path(self):
        path = self.locations().candidate
        with patch.object(
            backend, "_powershell", return_value='{"fixed":"value"}'
        ) as io:
            self.assertEqual(storage._read_bounded(path), {"fixed": "value"})
        script, payload = io.call_args.args
        self.assertEqual(payload, {"path": str(path)})
        self.assertEqual(script, storage._BOUNDED_READ_SCRIPT)
        self.assertNotIn("ReadAllText", script)
        self.assertNotIn("WriteAllText", script)
        for marker in (
            "131072",
            "byte[] 131073",
            "32768",
            "[IO.FileShare]::Read",
            "ReparsePoint",
            "UTF8Encoding]::new($false,$true)",
            "ZeroFreeBSTR",
            "$secure.Dispose()",
            "$stream.Dispose()",
        ):
            self.assertIn(marker, script)

    def test_decoder_rejects_nonabsolute_path_before_process(self):
        with patch.object(backend, "_powershell") as io:
            for path in ("not-a-path", Path("relative-only"), None):
                self.assert_unavailable(lambda: storage._read_bounded(path))
            io.assert_not_called()

    def test_decoder_rejects_duplicate_nested_keys_constants_and_nonobjects(self):
        for text in (
            '{"a":1,"a":2}',
            '{"nested":{"a":1,"a":2}}',
            '{"a":NaN}',
            '{"a":Infinity}',
            "[]",
            "null",
            "false",
            "1",
            '"text"',
            "{broken}",
        ):
            with patch.object(backend, "_powershell", return_value=text):
                self.assert_unavailable(
                    lambda: storage._read_bounded(self.locations().candidate)
                )

    def test_decoder_enforces_plaintext_return_bounds_and_type(self):
        for value in (None, b"{}", "", "x" * 32769):
            with patch.object(backend, "_powershell", return_value=value):
                self.assert_unavailable(
                    lambda: storage._read_bounded(self.locations().candidate)
                )
        text = '{"x":"' + "x" * (32768 - len('{"x":""}')) + '"}'
        with patch.object(backend, "_powershell", return_value=text):
            self.assertEqual(len(text), 32768)
            self.assertIsInstance(
                storage._read_bounded(self.locations().candidate), dict
            )

    def test_decoder_sanitizes_process_utf8_and_sensitive_failure_details(self):
        for error in (
            RuntimeError("fabricated-sensitive-body"),
            UnicodeDecodeError("utf-8", b"\xff", 0, 1, "fabricated-invalid"),
        ):
            with patch.object(backend, "_powershell", side_effect=error):
                self.assert_unavailable(
                    lambda: storage._read_bounded(self.locations().candidate)
                )

    def test_client_reads_only_fixed_client_and_returns_hash(self):
        locations = self.locations()
        value = {
            "project_id": "growthtwin-ads-test",
            "type": "web",
            "client_id": "fabricated.apps.googleusercontent.com",
            "client_secret": "fabricated-secret",
        }
        with patch.object(storage, "_read_bounded", return_value=value) as read:
            key = storage._client_key(locations)
        read.assert_called_once_with(locations.client)
        self.assertEqual(key, hashlib.sha256(value["client_id"].encode()).hexdigest())
        self.assertNotIn(value["client_secret"], key)

    def test_client_configuration_shapes_fail_closed(self):
        value = {
            "project_id": "growthtwin-ads-test",
            "type": "web",
            "client_id": "fabricated.apps.googleusercontent.com",
            "client_secret": "fabricated-secret",
        }
        for changes in (
            {"project_id": "different"},
            {"type": "installed"},
            {"client_id": "not-a-client"},
            {"client_id": None},
            {"client_secret": ""},
            {"client_secret": None},
            {"client_secret": "x" * 8193},
        ):
            with patch.object(storage, "_read_bounded", return_value=value | changes):
                self.assert_unavailable(lambda: storage._client_key(self.locations()))

    def test_legacy_presence_is_metadata_only_and_missing_is_not_error(self):
        locations = self.locations()
        with (
            patch.object(
                Path,
                "stat",
                return_value=SimpleNamespace(
                    st_mode=stat.S_IFREG, st_file_attributes=0
                ),
            ) as metadata,
            patch.object(storage, "_read_bounded") as read,
            patch.object(backend, "_powershell") as process,
        ):
            self.assertIs(storage._legacy_present(locations), True)
            metadata.assert_called_once_with(follow_symlinks=False)
            read.assert_not_called()
            process.assert_not_called()
        with patch.object(Path, "stat", side_effect=FileNotFoundError):
            self.assertIs(storage._legacy_present(locations), False)

    def test_legacy_inaccessible_directory_symlink_or_reparse_is_not_absence(self):
        locations = self.locations()
        for error in (PermissionError, OSError):
            with patch.object(Path, "stat", side_effect=error):
                self.assert_unavailable(lambda: storage._legacy_present(locations))
        for mode, attributes in (
            (stat.S_IFDIR, 0),
            (stat.S_IFLNK, 0),
            (stat.S_IFREG, stat.FILE_ATTRIBUTE_REPARSE_POINT),
        ):
            with patch.object(
                Path,
                "stat",
                return_value=SimpleNamespace(
                    st_mode=mode, st_file_attributes=attributes
                ),
            ):
                self.assert_unavailable(lambda: storage._legacy_present(locations))
