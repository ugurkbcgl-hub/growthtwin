"""Synthetic, network-free checks for the OAuth preparation boundary."""

import base64
import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import parse_qs, urlencode, urlsplit

from django.test import SimpleTestCase

from .google_oauth import (
    LOCAL_REDIRECT_URI,
    AuthorizationRejected,
    LocalAuthorizationStore,
)
from .logging import OAuthCallbackFilter


class AuthorizationTests(SimpleTestCase):
    def setUp(self):
        self.now = 100
        self.store = LocalAuthorizationStore(clock=lambda: self.now)
        self.binding = ("owner-1", "workspace-1", "session-1")
        self.url = self.store.begin(
            client_id="synthetic.apps.googleusercontent.com", binding=self.binding
        )
        self.params = parse_qs(urlsplit(self.url).query)
        self.query = urlencode(
            {"state": self.params["state"][0], "code": "synthetic-code"}
        )

    def test_fixed_destination_and_pkce(self):
        self.assertEqual(urlsplit(self.url).netloc, "accounts.google.com")
        self.assertEqual(self.params["redirect_uri"], [LOCAL_REDIRECT_URI])
        result = self.store.consume(binding=self.binding, query=self.query)
        challenge = (
            base64.urlsafe_b64encode(hashlib.sha256(result.verifier.encode()).digest())
            .decode()
            .rstrip("=")
        )
        self.assertEqual(self.params["code_challenge"], [challenge])
        self.assertEqual(result.code, "synthetic-code")
        self.assertNotIn(result.code, repr(result))
        self.assertNotIn(result.verifier, repr(result))

    def test_replay_rejected(self):
        self.store.consume(binding=self.binding, query=self.query)
        with self.assertRaises(AuthorizationRejected):
            self.store.consume(binding=self.binding, query=self.query)

    def test_each_binding_component_is_required(self):
        for index in range(3):
            other = list(self.binding)
            other[index] = "other"
            with self.assertRaises(AuthorizationRejected):
                self.store.consume(binding=tuple(other), query=self.query)
        self.store.consume(binding=self.binding, query=self.query)

    def test_expiry(self):
        self.now += 300
        with self.assertRaises(AuthorizationRejected):
            self.store.consume(binding=self.binding, query=self.query)

    def test_invalid_response_consumes_attempt(self):
        for query in (
            "state=wrong&code=synthetic-code",
            self.query + "&code=duplicate",
            self.query + "&error=access_denied",
            "state=%C4%B1&code=synthetic-code",
            "x=" + "a" * 8192,
        ):
            with self.subTest(query_kind=query[:12]):
                self.setUp()
                with self.assertRaises(AuthorizationRejected) as caught:
                    self.store.consume(binding=self.binding, query=query)
                self.assertNotIn("synthetic-code", str(caught.exception))
                with self.assertRaises(AuthorizationRejected):
                    self.store.consume(binding=self.binding, query=self.query)

    def test_restart_and_replacement_invalidate_old_attempt(self):
        with self.assertRaises(AuthorizationRejected):
            LocalAuthorizationStore().consume(binding=self.binding, query=self.query)
        self.store.begin(
            client_id="synthetic.apps.googleusercontent.com", binding=self.binding
        )
        with self.assertRaises(AuthorizationRejected):
            self.store.consume(binding=self.binding, query=self.query)

    def test_concurrent_callback_has_one_winner(self):
        def consume(_):
            try:
                self.store.consume(binding=self.binding, query=self.query)
                return True
            except AuthorizationRejected:
                return False

        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sum(pool.map(consume, range(2))), 1)

    def test_invalid_client_is_rejected(self):
        with self.assertRaises(AuthorizationRejected):
            self.store.begin(client_id="invalid", binding=self.binding)


class CallbackLoggingTests(SimpleTestCase):
    def test_callback_records_dropped_normal_records_retained(self):
        for message, expected in (
            ("GET /connections/google/callback?code=synthetic", False),
            ('"GET /connections/google/callback/?code=synthetic HTTP/1.1"', False),
            ("GET %2Fconnections%2Fgoogle%2Fcallback%2F?state=synthetic", False),
            ("GET /health/ HTTP/1.1", True),
        ):
            record = logging.LogRecord(
                "django.server", 20, "", 0, "%s", (message,), None
            )
            self.assertEqual(OAuthCallbackFilter().filter(record), expected)

    def test_configured_server_handler_drops_callback(self):
        logger = logging.getLogger("django.server")
        self.assertFalse(logger.propagate)
        self.assertTrue(logger.handlers)
        record = logging.LogRecord(
            logger.name,
            20,
            "",
            0,
            "GET /connections/google/callback/?code=synthetic",
            (),
            None,
        )
        for handler in logger.handlers:
            self.assertFalse(handler.filter(record))
