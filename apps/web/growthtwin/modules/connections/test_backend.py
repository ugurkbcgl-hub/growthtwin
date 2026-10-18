"""Synthetic OAuth backend checks: all transport and credential storage mocked."""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs

from django.test import SimpleTestCase, override_settings

from . import backend
from .google_oauth import ADS_SCOPE, LOCAL_REDIRECT_URI, AuthorizationCode


@override_settings(
    DEBUG=False,
    GOOGLE_ADS_LOCAL_OAUTH_ENABLED=True,
    GOOGLE_ADS_LOCAL_OWNER_ID="1",
    GOOGLE_ADS_LOCAL_WORKSPACE_ID="2",
)
class LocalBackendTests(SimpleTestCase):
    binding = ("1", "2", "synthetic-session")

    def setUp(self):
        self.code = AuthorizationCode("fabricated-code", "fabricated-verifier")
        self.token = {
            "token_type": "Bearer",
            "refresh_token": "fabricated-refresh",
            "access_token": "fabricated-access",
            "scope": ADS_SCOPE,
        }
        self.client = {
            "project_id": "growthtwin-ads-test",
            "type": "web",
            "client_id": "fabricated.apps.googleusercontent.com",
            "client_secret": "fabricated-secret",
        }

    def test_feature_debug_and_platform_gates_prevent_storage_or_network(self):
        for enabled, debug, platform in (
            (False, False, "nt"),
            (True, True, "nt"),
            (True, False, "posix"),
        ):
            with self.subTest(enabled=enabled, debug=debug, platform=platform):
                with override_settings(
                    GOOGLE_ADS_LOCAL_OAUTH_ENABLED=enabled, DEBUG=debug
                ):
                    with (
                        patch.object(backend.os, "name", platform),
                        patch.object(backend, "_token_path") as path,
                        patch.object(backend, "_read") as read,
                    ):
                        for operation in (
                            lambda: backend.exchange_and_store(self.code, self.binding),
                            lambda: backend.disconnect(self.binding),
                            lambda: backend.connection_exists(self.binding),
                            backend.load_client_id,
                        ):
                            with self.assertRaises(backend.ConnectionUnavailable):
                                operation()
                        path.assert_not_called()
                        read.assert_not_called()

    def test_storage_identity_binds_owner_workspace_and_survives_session_change(self):
        with patch.dict(backend.os.environ, {"LOCALAPPDATA": "synthetic-data"}):
            first = backend._token_path(self.binding)
            self.assertEqual(first, backend._token_path(("1", "2", "new-session")))
            for binding in (
                ("3", "2", "s"),
                ("1", "3", "s"),
                ("1", "2", ""),
                ("1", "2"),
                ["1", "2", "s"],
                None,
            ):
                with self.subTest(binding=binding):
                    with self.assertRaises(backend.ConnectionUnavailable):
                        backend._token_path(binding)

    def test_exchange_stores_refresh_only_and_uses_fixed_callback(self):
        with (
            patch.object(backend, "_enabled"),
            patch.object(backend, "_token_path") as path,
            patch.object(backend, "_client", return_value=self.client),
            patch.object(backend, "_post", return_value=json.dumps(self.token)) as post,
            patch.object(backend, "_write") as write,
        ):
            path.return_value.exists.return_value = False
            backend.exchange_and_store(self.code, self.binding)
            endpoint, fields = post.call_args.args
            self.assertEqual(endpoint, "https://oauth2.googleapis.com/token")
            self.assertEqual(fields["redirect_uri"], LOCAL_REDIRECT_URI)
            self.assertEqual(fields["code_verifier"], self.code.verifier)
            self.assertEqual(fields["grant_type"], "authorization_code")
            write.assert_called_once_with(
                path.return_value,
                {"refresh_token": "fabricated-refresh", "scope": ADS_SCOPE},
            )

    def test_existing_credential_is_not_overwritten(self):
        with (
            patch.object(backend, "_enabled"),
            patch.object(backend, "_token_path") as path,
            patch.object(backend, "_client") as client,
            patch.object(backend, "_post") as post,
        ):
            path.return_value.exists.return_value = True
            with self.assertRaises(backend.ConnectionUnavailable):
                backend.exchange_and_store(self.code, self.binding)
            client.assert_not_called()
            post.assert_not_called()

    def test_client_requires_test_project_web_type_and_credentials(self):
        with (
            patch.object(backend, "_enabled"),
            patch.dict(backend.os.environ, {"LOCALAPPDATA": "synthetic-data"}),
            patch.object(backend, "_read") as read,
        ):
            read.return_value = self.client
            self.assertEqual(backend.load_client_id(), self.client["client_id"])
            for value in (
                [],
                None,
                {**self.client, "project_id": "unrelated-project"},
                {**self.client, "type": "installed"},
                {**self.client, "client_id": "not-a-google-client"},
                {**self.client, "client_secret": ""},
            ):
                with self.subTest(value=value):
                    read.return_value = value
                    with self.assertRaises(backend.ConnectionUnavailable):
                        backend.load_client_id()

    def test_missing_connection_disconnect_has_no_remote_effect(self):
        with (
            patch.object(backend, "_enabled"),
            patch.object(backend, "_token_path") as path,
            patch.object(backend, "_read") as read,
            patch.object(backend, "_post") as post,
        ):
            path.return_value.exists.return_value = False
            backend.disconnect(self.binding)
            read.assert_not_called()
            post.assert_not_called()
            path.return_value.unlink.assert_not_called()

    def test_invalid_provider_tokens_never_reach_storage(self):
        invalid = [[], None, "fabricated-sensitive-response"]
        for field, values in {
            "token_type": [None, 123, "Basic", ""],
            "refresh_token": [None, 123, ""],
            "access_token": [None, 123, ""],
            "scope": [None, 123, "", "openid", ADS_SCOPE + " openid"],
        }.items():
            invalid.extend([{**self.token, field: value} for value in values])
        with (
            patch.object(backend, "_enabled"),
            patch.object(backend, "_token_path") as path,
            patch.object(backend, "_client", return_value=self.client),
            patch.object(backend, "_post") as post,
            patch.object(backend, "_write") as write,
        ):
            path.return_value.exists.return_value = False
            for value in invalid:
                with self.subTest(value=value):
                    post.return_value = json.dumps(value)
                    with self.assertRaises(backend.ConnectionUnavailable) as raised:
                        backend.exchange_and_store(self.code, self.binding)
                    self.assertNotIn(
                        "fabricated-sensitive-response", str(raised.exception)
                    )
            write.assert_not_called()

    def test_transport_disables_redirects_and_uses_bounded_post(self):
        response = MagicMock(status=200)
        response.read.return_value = b"{}"
        with patch.object(backend, "build_opener") as opener:
            opener.return_value.open.return_value.__enter__.return_value = response
            self.assertEqual(
                backend._post(
                    "https://oauth2.googleapis.com/token", {"code": "fabricated + code"}
                ),
                b"{}",
            )
            handler = opener.call_args.args[0]
            self.assertIsInstance(handler, backend._NoRedirect)
            self.assertIsNone(
                handler.redirect_request(
                    None, None, 302, "", {}, "https://other.invalid"
                )
            )
            request = opener.return_value.open.call_args.args[0]
            self.assertEqual(request.method, "POST")
            self.assertEqual(
                parse_qs(request.data.decode()), {"code": ["fabricated + code"]}
            )
            self.assertEqual(opener.return_value.open.call_args.kwargs, {"timeout": 20})
            response.read.assert_called_once_with(65537)

    def test_unapproved_endpoint_is_rejected_before_network(self):
        with patch.object(backend, "build_opener") as opener:
            for endpoint in (
                "https://other.invalid/token",
                "http://oauth2.googleapis.com/token",
                "https://oauth2.googleapis.com/token?redirect=other",
                "https://oauth2.googleapis.com/token/",
            ):
                with self.subTest(endpoint=endpoint):
                    with self.assertRaises(backend.ConnectionUnavailable):
                        backend._post(endpoint, {"token": "fabricated-token"})
            opener.assert_not_called()

    def test_failed_write_attempts_revocation_and_sanitizes_revoke_failure(self):
        with (
            patch.object(backend, "_enabled"),
            patch.object(backend, "_token_path") as path,
            patch.object(backend, "_client", return_value=self.client),
            patch.object(
                backend,
                "_write",
                side_effect=backend.ConnectionUnavailable("fabricated-write-secret"),
            ) as write,
            patch.object(backend, "_post") as post,
        ):
            path.return_value.exists.return_value = False
            for revoke_result in (
                b"",
                backend.ConnectionUnavailable("fabricated-revoke-secret"),
            ):
                with self.subTest(revocation_succeeds=isinstance(revoke_result, bytes)):
                    post.reset_mock()
                    write.reset_mock()
                    post.side_effect = [json.dumps(self.token), revoke_result]
                    with self.assertRaises(backend.ConnectionUnavailable) as raised:
                        backend.exchange_and_store(self.code, self.binding)
                    write.assert_called_once()
                    self.assertEqual(post.call_count, 2)
                    self.assertEqual(
                        post.call_args.args,
                        (
                            "https://oauth2.googleapis.com/revoke",
                            {"token": "fabricated-access"},
                        ),
                    )
                    self.assertIn("Authorization was not saved", str(raised.exception))
                    self.assertNotIn("fabricated", str(raised.exception))
                    self.assertTrue(raised.exception.__suppress_context__)

    def test_invalid_scope_revokes_received_access_token_without_storage(self):
        with (
            patch.object(backend, "_enabled"),
            patch.object(backend, "_token_path") as path,
            patch.object(backend, "_client", return_value=self.client),
            patch.object(backend, "_write") as write,
            patch.object(backend, "_post") as post,
        ):
            path.return_value.exists.return_value = False
            post.side_effect = [json.dumps({**self.token, "scope": "openid"}), b""]
            with self.assertRaises(backend.ConnectionUnavailable):
                backend.exchange_and_store(self.code, self.binding)
            write.assert_not_called()
            self.assertEqual(
                post.call_args.args,
                (
                    "https://oauth2.googleapis.com/revoke",
                    {"token": "fabricated-access"},
                ),
            )

    def test_transport_errors_and_oversized_bodies_are_sanitized(self):
        with patch.object(backend, "build_opener") as opener:
            for status, body in (
                (200, b"x" * 65537),
                (302, b"secret"),
                (500, b"secret"),
            ):
                response = MagicMock(status=status)
                response.read.return_value = body
                opener.return_value.open.return_value.__enter__.return_value = response
                with self.assertRaises(backend.ConnectionUnavailable):
                    backend._post("https://oauth2.googleapis.com/token", {})
            opener.return_value.open.side_effect = RuntimeError("fabricated-secret")
            with self.assertRaises(backend.ConnectionUnavailable) as raised:
                backend._post("https://oauth2.googleapis.com/token", {})
            self.assertNotIn("fabricated-secret", str(raised.exception))

    def test_revoke_succeeds_before_local_deletion_and_failure_keeps_file(self):
        with (
            patch.object(backend, "_enabled"),
            patch.object(backend, "_token_path") as path,
            patch.object(backend, "_read", return_value=self.token),
            patch.object(backend, "_post") as post,
        ):
            path.return_value.exists.return_value = True
            events = []
            post.side_effect = lambda *args: events.append("revoke")
            path.return_value.unlink.side_effect = lambda: events.append("delete")
            backend.disconnect(self.binding)
            self.assertEqual(events, ["revoke", "delete"])
            post.assert_called_once_with(
                "https://oauth2.googleapis.com/revoke", {"token": "fabricated-refresh"}
            )
            path.return_value.unlink.reset_mock()
            post.side_effect = backend.ConnectionUnavailable("Unavailable")
            with self.assertRaises(backend.ConnectionUnavailable):
                backend.disconnect(self.binding)
            path.return_value.unlink.assert_not_called()

    def test_dpapi_command_uses_stdin_and_sanitizes_failure(self):
        with (
            patch.object(backend, "_enabled"),
            patch.dict(backend.os.environ, {"SystemRoot": "synthetic-windows"}),
            patch.object(backend.subprocess, "CREATE_NO_WINDOW", 0, create=True),
            patch.object(backend.subprocess, "run") as run,
        ):
            run.return_value = SimpleNamespace(returncode=0, stdout="encrypted-output")
            self.assertEqual(
                backend._powershell("synthetic-script", {"value": "fabricated-secret"}),
                "encrypted-output",
            )
            self.assertNotIn("fabricated-secret", str(run.call_args.args))
            self.assertIn("fabricated-secret", run.call_args.kwargs["input"])
            run.side_effect = RuntimeError("fabricated-secret")
            with self.assertRaises(backend.ConnectionUnavailable) as raised:
                backend._powershell("synthetic-script", {})
            self.assertNotIn("fabricated-secret", str(raised.exception))
