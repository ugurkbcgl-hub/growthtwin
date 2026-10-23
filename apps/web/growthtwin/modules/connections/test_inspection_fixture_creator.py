"""Fixture creator admission and scalar reporting; no Windows/credential I/O."""

import contextlib
import copy
import io
import json
import os
import socket
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

from django.db.backends.base.base import BaseDatabaseWrapper
from django.test import SimpleTestCase

from scripts import rehearse_inspection_fixture as creator


class InspectionFixtureCreatorTests(SimpleTestCase):
    def test_parser_accepts_only_the_four_fixed_scenarios(self):
        for scenario in ("match", "client-changed", "invalid-envelope", "unreadable"):
            with self.subTest(scenario=scenario):
                self.assertEqual(creator._parse_scenario([scenario]), scenario)

    def test_parser_rejects_paths_extra_options_and_missing_scenario(self):
        for arguments in (
            [],
            ["unknown"],
            ["MATCH"],
            ["match", "match"],
            ["--path", "fabricated-private-path"],
            ["match", "--database", "fabricated-database"],
            ["C:\\fabricated\\candidate.dpapi"],
            ["match\n"],
        ):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                creator._parse_scenario(arguments)

    def test_scalar_report_has_exact_allowlisted_schema(self):
        report = creator._empty_report()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            creator._emit(report)
        self.assertEqual(json.loads(output.getvalue()), report)
        self.assertEqual(
            set(report),
            {
                "passed",
                "scenario",
                "stage",
                "disposition",
                "permit_state",
                "history_preserved",
                "cleanup_complete",
                "private_storage_verified",
                "session_count",
                "boundary_attempts",
                "client_reads",
                "candidate_reads",
                "replay_refused",
            },
        )
        self.assertTrue(
            all(type(value) in (str, bool, int) for value in report.values())
        )

    def test_report_refuses_unknown_sensitive_fields_without_printing_them(self):
        for key in (
            "session_key",
            "refresh_token",
            "path",
            "exception",
            "client_secret",
        ):
            report = creator._empty_report()
            report[key] = "fabricated-sensitive-value-must-never-print"
            output = io.StringIO()
            with self.subTest(key=key), contextlib.redirect_stdout(output):
                with self.assertRaises(ValueError):
                    creator._emit(report)
            self.assertEqual(output.getvalue(), "")

    def test_report_refuses_wrong_types_ranges_or_unapproved_strings_atomically(self):
        mutations = (
            ("passed", 1),
            ("history_preserved", "true"),
            ("cleanup_complete", []),
            ("private_storage_verified", None),
            ("replay_refused", 0),
            ("session_count", -2),
            ("session_count", 10001),
            ("boundary_attempts", -1),
            ("client_reads", True),
            ("candidate_reads", 1.0),
            ("scenario", "fabricated-secret"),
            ("stage", "fabricated-secret"),
            ("disposition", "fabricated-secret"),
            ("permit_state", "fabricated-secret"),
        )
        for key, value in mutations:
            report = copy.deepcopy(creator._empty_report())
            report[key] = value
            output = io.StringIO()
            with self.subTest(key=key, value=value), contextlib.redirect_stdout(output):
                with self.assertRaises(ValueError):
                    creator._emit(report)
            self.assertEqual(output.getvalue(), "")

    def test_report_requires_every_fixed_key(self):
        for key in creator._empty_report():
            report = creator._empty_report()
            del report[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                creator._emit(report)

    def assert_admission_refusal(self, argv, platform):
        before = dict(os.environ)
        output = io.StringIO()
        with (
            patch.object(sys, "argv", ["fabricated-fixture-command", *argv]),
            patch.object(os, "name", platform),
            patch(
                "django.setup", side_effect=AssertionError("Setup forbidden")
            ) as setup,
            patch.object(
                tempfile, "mkdtemp", side_effect=AssertionError("Files forbidden")
            ) as files,
            patch.object(
                creator, "_exercise", side_effect=AssertionError("Exercise forbidden")
            ) as exercise,
            contextlib.redirect_stdout(output),
        ):
            self.assertEqual(creator.main(), 2)
        self.assertEqual(dict(os.environ), before)
        setup.assert_not_called()
        files.assert_not_called()
        exercise.assert_not_called()
        report = json.loads(output.getvalue())
        self.assertFalse(report["passed"])
        self.assertEqual(report["stage"], "admission")
        self.assertEqual(report["boundary_attempts"], 0)

    def test_invalid_cli_refuses_before_startup_environment_or_files(self):
        self.assert_admission_refusal([], "nt")
        self.assert_admission_refusal(["match", "fabricated-extra"], "nt")

    def test_non_windows_refuses_before_startup_environment_or_files(self):
        self.assert_admission_refusal(["match"], "posix")

    def test_initialized_django_refuses_reusing_current_database_or_environment(self):
        self.assert_admission_refusal(["match"], "nt")

    def assert_startup_failure(self, setup_side_effect, expected_attempts):
        environment = dict(os.environ)
        output = io.StringIO()
        with (
            patch.object(sys, "argv", ["fabricated-fixture-command", "match"]),
            patch.object(sys, "path", list(sys.path)),
            patch.object(os, "name", "nt"),
            patch.object(creator, "Path") as startup_path,
            patch("django.conf.settings", SimpleNamespace(configured=False)),
            patch("django.apps.apps.ready", False),
            patch("django.setup", side_effect=setup_side_effect),
            patch.object(creator, "_exercise") as exercise,
            patch.object(tempfile, "mkdtemp") as files,
            contextlib.redirect_stdout(output),
        ):
            # Only the Windows admission gate is simulated. Never construct a
            # WindowsPath on Linux CI for this unrelated startup import path.
            startup_path.return_value.resolve.return_value.parent.parent = (
                "fabricated-startup-module-root"
            )
            self.assertEqual(creator.main(), 1)
        self.assertEqual(dict(os.environ), environment)
        exercise.assert_not_called()
        files.assert_not_called()
        lines = output.getvalue().splitlines()
        self.assertEqual(len(lines), 1)
        report = json.loads(lines[0])
        self.assertFalse(report["passed"])
        self.assertEqual(report["stage"], "setup")
        self.assertEqual(report["boundary_attempts"], expected_attempts)
        self.assertNotIn("fabricated-private-error", output.getvalue())

    def test_startup_failure_emits_only_scalar_report_and_restores_environment(self):
        self.assert_startup_failure(ValueError("fabricated-private-error"), 0)

    def test_swallowed_startup_database_attempt_refuses_before_fixture_creation(self):
        def attempted_database():
            try:
                BaseDatabaseWrapper.ensure_connection(None)
            except AssertionError:
                pass

        self.assert_startup_failure(attempted_database, 1)

    def test_startup_network_attempt_is_blocked_and_counted(self):
        def attempted_network():
            socket.create_connection(("fabricated.invalid", 443))

        self.assert_startup_failure(attempted_network, 1)

    def test_swallowed_startup_network_attempt_refuses_before_fixture_creation(self):
        def attempted_network():
            try:
                socket.create_connection(("fabricated.invalid", 443))
            except AssertionError:
                pass

        self.assert_startup_failure(attempted_network, 1)
