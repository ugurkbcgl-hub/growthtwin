"""Private fixture file admission with native boundaries replaced throughout."""

import json
import os
import stat
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from scripts import inspection_fixture_files as files


class FixtureFilesTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="gwt-files-unit-")
        self.addCleanup(self.temp.cleanup)
        self.appdata = Path(self.temp.name).resolve()
        (self.appdata / "Temp").mkdir()
        self.calls = []
        self.real_native = files._native
        self.guards = [
            patch.object(files, "_ORIGINAL_APPDATA", str(self.appdata)),
            patch.object(files, "_HOMES", {}),
            patch.object(files, "_windows"),
            patch.object(files, "_native", side_effect=self.native),
        ]
        for guard in self.guards:
            guard.start()
            self.addCleanup(guard.stop)

    def native(self, script, payload):
        self.calls.append((script, dict(payload)))
        if script == files._ENCRYPT:
            with Path(payload["path"]).open("xb") as output:
                output.write(b"fabricated-ciphertext-not-real-dpapi")

    def home(self):
        return files.create_home()

    def test_root_secured_while_empty_before_any_bytes_and_registered(self):
        home = self.home()
        self.assertEqual(home.parent, self.appdata / "Temp")
        self.assertTrue(home.name.startswith("gwt-inspection-once-fixture-"))
        self.assertEqual(list(home.iterdir()), [])
        self.assertEqual(self.calls[0], (files._SECURE, {"path": str(home)}))
        self.assertEqual(self.calls[1], (files._ACL_CHECK, {"path": str(home)}))
        self.assertIn(home, files._HOMES)
        self.assertTrue(files.cleanup(home, [], []))
        self.assertFalse(home.exists())

    def test_unknown_existing_directory_never_mutates_acl(self):
        unknown = self.appdata / "unknown"
        unknown.mkdir()
        with self.assertRaises(ValueError):
            files.make_private_directory(unknown)
        self.assertEqual(self.calls, [])

    def test_existing_descendant_is_not_adopted_or_secured(self):
        home = self.home()
        existing = home / "preexisting"
        existing.mkdir()
        count = len(self.calls)
        with self.assertRaises(FileExistsError):
            files.make_private_directory(existing)
        self.assertNotIn(existing, files._HOMES[home].directories)
        self.assertEqual(len(self.calls), count + 1)  # Parent ACL observation only.

    def test_private_parent_admission_precedes_encryption_and_existing_refuses(self):
        home = self.home()
        appdata = files.make_private_directory(home / "appdata")
        root = files.make_private_directory(appdata / "GrowthTwinsecrets")
        path = root / "fixed.dpapi"
        start = len(self.calls)
        files.encrypt_new(path, {"fabricated": "İstanbul"})
        self.assertEqual(self.calls[start], (files._ACL_CHECK, {"path": str(root)}))
        self.assertEqual(self.calls[start + 1][0], files._ENCRYPT)
        self.assertEqual(
            json.loads(self.calls[start + 1][1]["text"]), {"fabricated": "İstanbul"}
        )
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            files.encrypt_new(path, {"fabricated": "changed"})
        self.assertEqual(path.read_bytes(), before)
        self.assertTrue(
            files.cleanup(home, [path, root / "missing.dpapi"], [appdata, root])
        )

    def test_acl_failure_stops_before_encrypted_bytes(self):
        home = self.home()
        path = home / "fixed.dpapi"
        with patch.object(
            files, "assert_private", side_effect=ValueError("fabricated")
        ):
            with self.assertRaises(ValueError):
                files.encrypt_new(path, {"fabricated": True})
        self.assertFalse(path.exists())
        self.assertFalse(any(script == files._ENCRYPT for script, _ in self.calls))

    def test_unknown_or_parent_traversal_encryption_refuses(self):
        home = self.home()
        for path in (self.appdata / "outside.dpapi", home / ".." / "outside.dpapi"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                files.encrypt_new(path, {"fabricated": True})

    def test_replaced_root_identity_refuses_before_mutation(self):
        home = self.home()
        record = files._HOMES[home]
        record.identity = ("different", "fabricated")
        before = len(self.calls)
        with self.assertRaises(ValueError):
            files.make_private_directory(home / "appdata")
        self.assertEqual(len(self.calls), before)

    def test_replaced_registered_child_directory_refuses(self):
        home = self.home()
        appdata = files.make_private_directory(home / "appdata")
        files._HOMES[home].directories[appdata] = ("changed", "fabricated")
        before = len(self.calls)
        with self.assertRaises(ValueError):
            files.make_private_directory(appdata / "GrowthTwinsecrets")
        self.assertEqual(len(self.calls), before)

    def test_reparse_metadata_is_refused_before_native_access(self):
        metadata = SimpleNamespace(
            st_mode=stat.S_IFDIR,
            st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT,
        )
        with patch.object(Path, "stat", return_value=metadata):
            with self.assertRaises(ValueError):
                files.no_reparse(self.appdata)
        self.assertEqual(self.calls, [])

    def test_cleanup_unknown_file_refuses_before_deleting_known_file(self):
        home = self.home()
        known = home / "known.sqlite3"
        known.write_bytes(b"fabricated-db")
        outside = self.appdata / "outside"
        outside.write_bytes(b"retain")
        with self.assertRaises(ValueError):
            files.cleanup(home, [known, outside], [])
        self.assertTrue(known.exists())
        self.assertEqual(outside.read_bytes(), b"retain")

    def test_unexpected_journal_is_retained_and_prevents_cleanup_success(self):
        home = self.home()
        db = home / "fixture.sqlite3"
        journal = home / "fixture.sqlite3-journal"
        db.write_bytes(b"fabricated-db")
        journal.write_bytes(b"retain-unexpected")
        with self.assertRaises(OSError):
            files.cleanup(home, [db], [])
        self.assertEqual(journal.read_bytes(), b"retain-unexpected")
        self.assertIn(home, files._HOMES)

    def test_cleanup_directory_in_file_list_refuses(self):
        home = self.home()
        folder = files.make_private_directory(home / "appdata")
        with self.assertRaises(ValueError):
            files.cleanup(home, [folder], [])
        self.assertTrue(folder.is_dir())

    def test_explicit_companion_cleanup_is_refused_without_deleting_it(self):
        home = self.home()
        journal = home / "fixture.sqlite3-journal"
        journal.write_bytes(b"retain-unexpected")
        with self.assertRaisesRegex(ValueError, "SQLite companion"):
            files.cleanup(home, [journal], [])
        self.assertEqual(journal.read_bytes(), b"retain-unexpected")

    def test_cleanup_private_acl_failure_retains_file(self):
        home = self.home()
        path = home / "fixed"
        path.write_bytes(b"fabricated")
        with patch.object(files, "assert_private", side_effect=ValueError):
            with self.assertRaises(ValueError):
                files.cleanup(home, [path], [])
        self.assertEqual(path.read_bytes(), b"fabricated")

    def test_encryption_rejects_non_object_or_nonfinite_payload(self):
        home = self.home()
        for value in ([], {"value": float("nan")}, {"payload": "x" * 32768}):
            with self.subTest(value_type=type(value)), self.assertRaises(ValueError):
                files.encrypt_new(home / "fixed.dpapi", value)
        self.assertFalse((home / "fixed.dpapi").exists())

    def test_native_failure_suppresses_process_exception_and_output(self):
        # Undo just the native replacement; the Windows/process boundary stays mocked.
        with (
            patch.dict(os.environ, {"SystemRoot": str(self.appdata)}),
            patch.object(
                subprocess,
                "run",
                side_effect=RuntimeError("fabricated-sensitive-error"),
            ),
        ):
            native = self.real_native
            with self.assertRaisesRegex(
                ValueError, "Fixture native operation refused"
            ) as caught:
                native(files._ACL_CHECK, {"path": "fabricated"})
        self.assertNotIn("sensitive", str(caught.exception))

    def test_native_only_accepts_exact_boolean_success_and_finite_hidden_process(self):
        native = self.real_native
        with patch.dict(os.environ, {"SystemRoot": str(self.appdata)}):
            for stdout in ('{"ok":false}', "raw fabricated", '{"ok":true}\n'):
                with (
                    self.subTest(stdout=stdout),
                    patch.object(
                        subprocess,
                        "run",
                        return_value=SimpleNamespace(returncode=0, stdout=stdout),
                    ),
                    self.assertRaises(ValueError),
                ):
                    native(files._ACL_CHECK, {"path": "fabricated"})
            with patch.object(
                subprocess,
                "run",
                return_value=SimpleNamespace(returncode=0, stdout='{"ok":true}'),
            ) as runner:
                native(files._ACL_CHECK, {"path": "fabricated"})
            self.assertEqual(runner.call_args.kwargs["timeout"], 20)
            self.assertTrue(runner.call_args.kwargs["capture_output"])
            self.assertIn("-NonInteractive", runner.call_args.args[0])
