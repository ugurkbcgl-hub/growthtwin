"""Fail-closed account identity check without external requests."""

import json
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from . import backend, verification, views
from .google_oauth import ADS_SCOPE
from .test_views import LocalConnectionViewsTests


@override_settings(
    GOOGLE_ADS_LOCAL_TEST_CUSTOMER_ID="1111111111",
    GOOGLE_ADS_LOCAL_TEST_MANAGER_ID="2222222222",
)
class TestAccountVerificationTests(SimpleTestCase):
    def test_only_matching_nonmanager_test_child_is_accepted(self):
        for customer, accepted in (
            ({"id": "1111111111", "testAccount": True}, True),
            ({"id": "1111111111", "testAccount": False}, False),
            ({"id": "1111111111", "testAccount": True, "manager": True}, False),
            ({"id": "3333333333", "testAccount": True}, False),
        ):
            with (
                self.subTest(customer=customer),
                patch.object(backend, "_enabled"),
                patch.object(backend, "_token_path"),
                patch.object(verification, "configuration_key", return_value="key"),
                patch.object(
                    backend,
                    "_read",
                    return_value={"scope": ADS_SCOPE, "refresh_token": "fake"},
                ),
                patch.object(
                    backend,
                    "_client",
                    return_value={"client_id": "fake", "client_secret": "fake"},
                ),
                patch.object(
                    backend,
                    "_post",
                    return_value=json.dumps(
                        {"access_token": "fake", "token_type": "Bearer"}
                    ),
                ),
                patch.object(verification, "build_opener") as opener,
            ):
                response = opener.return_value.open.return_value.__enter__.return_value
                response.status = 200
                response.read.return_value = json.dumps(
                    {"results": [{"customer": customer}]}
                ).encode()
                if accepted:
                    self.assertEqual(verification.verify(("1", "1", "s")), "key")
                else:
                    with self.assertRaises(backend.ConnectionUnavailable):
                        verification.verify(("1", "1", "s"))
                request = opener.return_value.open.call_args.args[0]
                self.assertEqual(
                    request.full_url,
                    "https://googleads.googleapis.com/v25/customers/1111111111/googleAds:search",
                )
                self.assertEqual(
                    json.loads(request.data), {"query": verification.QUERY}
                )

    @override_settings(GOOGLE_ADS_LOCAL_TEST_CUSTOMER_ID="")
    def test_missing_target_prevents_network(self):
        with patch.object(backend, "_enabled"), patch.object(backend, "_post") as post:
            with self.assertRaises(backend.ConnectionUnavailable):
                verification.verify(("1", "1", "s"))
            post.assert_not_called()


class VerificationViewsTests(LocalConnectionViewsTests):
    def test_status_invalidates_expired_or_changed_evidence_without_network(self):
        self.mock_backend.connection_exists.return_value = True
        for observed_at, key, expected in (
            (1000, "key", True),
            (399, "key", False),
            (1001, "key", False),
            (1000, "old", False),
        ):
            self.session["google_test_verification"] = {"key": key, "at": observed_at}
            with (
                patch.object(views.time, "time", return_value=1000),
                patch.object(verification, "configuration_key", return_value="key"),
                patch.object(verification, "verify") as verify,
            ):
                response = views.status(self.request())
                self.assertEqual("son 10 dakika" in response.content.decode(), expected)
                verify.assert_not_called()
                self.assertEqual("google_test_verification" in self.session, expected)

    def test_verification_requires_post_and_csrf(self):
        self.assertEqual(views.verify_test_account(self.request()).status_code, 405)
        request = self.request("post")
        request._dont_enforce_csrf_checks = False
        self.assertEqual(views.verify_test_account(request).status_code, 403)

    def test_success_and_failure_replace_session_evidence(self):
        with patch.object(verification, "verify", return_value="safe-key"):
            views.verify_test_account(self.request("post"))
        self.assertEqual(self.session["google_test_verification"]["key"], "safe-key")
        with patch.object(verification, "verify", side_effect=RuntimeError("PRIVATE")):
            response = views.verify_test_account(self.request("post"))
        self.assertEqual(response["Location"], views.STATUS_PATH)
        self.assertNotIn("google_test_verification", self.session)
        self.assertNotIn("PRIVATE", str(dict(self.session)))
