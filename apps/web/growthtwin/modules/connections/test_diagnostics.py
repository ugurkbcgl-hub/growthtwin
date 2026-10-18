"""Only allowlisted diagnostic categories may leave the OAuth transport."""

import io
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from django.test import SimpleTestCase

from . import backend


class DiagnosticTests(SimpleTestCase):
    def test_http_error_exposes_category_not_response(self):
        for body, expected in (
            (
                b'{"error":"invalid_client","error_description":"PRIVATE"}',
                "invalid_client",
            ),
            (b'{"error":"PRIVATE"}', "google_rejected"),
            (b"PRIVATE", "google_rejected"),
        ):
            with patch.object(backend, "build_opener") as opener:
                opener.return_value.open.side_effect = HTTPError(
                    "https://oauth2.googleapis.com/token",
                    400,
                    "PRIVATE",
                    {},
                    io.BytesIO(body),
                )
                with self.assertRaises(backend.ConnectionUnavailable) as error:
                    backend._post("https://oauth2.googleapis.com/token", {})
                self.assertEqual(error.exception.reason, expected)
                self.assertNotIn("PRIVATE", str(error.exception))

    def test_network_error_is_sanitized(self):
        with patch.object(backend, "build_opener") as opener:
            opener.return_value.open.side_effect = URLError("PRIVATE")
            with self.assertRaises(backend.ConnectionUnavailable) as error:
                backend._post("https://oauth2.googleapis.com/token", {})
            self.assertEqual(error.exception.reason, "network")
            self.assertNotIn("PRIVATE", str(error.exception))

    def test_unrecognized_category_is_not_retained(self):
        self.assertEqual(
            backend.ConnectionUnavailable(reason="PRIVATE").reason, "unavailable"
        )
