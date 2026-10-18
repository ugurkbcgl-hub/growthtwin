"""Isolated, mocked local authorization boundary checks."""

from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlencode, urlsplit

from django.contrib.sessions.backends.signed_cookies import SessionStore
from django.test import RequestFactory, SimpleTestCase, override_settings

from . import views
from .google_oauth import LocalAuthorizationStore


@override_settings(
    DEBUG=False,
    ALLOWED_HOSTS=["127.0.0.1", "testserver"],
    GOOGLE_ADS_LOCAL_OAUTH_ENABLED=True,
    GOOGLE_ADS_LOCAL_OWNER_ID="1",
    GOOGLE_ADS_LOCAL_WORKSPACE_ID="2",
)
class LocalConnectionViewsTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.session = SessionStore()
        self.session.create()
        self.session._session_key = "synthetic-session-key"
        self.workspace = patch.object(
            views, "get_workspace_for_owner", return_value=SimpleNamespace(pk=2)
        )
        self.workspace.start()
        self.addCleanup(self.workspace.stop)
        self.backend = patch.object(views, "backend", autospec=True)
        self.mock_backend = self.backend.start()
        self.addCleanup(self.backend.stop)
        # Exception types must remain real, not mocks.
        from .backend import ConnectionUnavailable

        self.mock_backend.ConnectionUnavailable = ConnectionUnavailable
        self.mock_backend.load_client_id.return_value = (
            "test.apps.googleusercontent.com"
        )
        self.mock_backend.connection_exists.return_value = False
        self.store = patch.object(
            views, "authorization_store", LocalAuthorizationStore()
        )
        self.store.start()
        self.addCleanup(self.store.stop)

    def request(self, method="get", path="/connections/google/", **extra):
        request = getattr(self.factory, method)(
            path, HTTP_HOST="127.0.0.1:8002", **extra
        )
        request.user = SimpleNamespace(pk=1, is_authenticated=True)
        request.session = self.session
        request._dont_enforce_csrf_checks = True
        return request

    def assert_private(self, response):
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(response["Referrer-Policy"], "no-referrer")

    def test_status_has_csrf_forms_and_test_only_warning(self):
        response = views.status(self.request())
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrfmiddlewaretoken", response.content.decode())
        self.assertIn("Reklam yayımlamaz", response.content.decode())
        self.assert_private(response)

    def test_disabled_debug_remote_forwarded_and_other_owner_denied(self):
        for setting in ({"GOOGLE_ADS_LOCAL_OAUTH_ENABLED": False}, {"DEBUG": True}):
            with self.settings(**setting):
                self.assertEqual(views.status(self.request()).status_code, 404)
        for extra in (
            {"REMOTE_ADDR": "10.0.0.1"},
            {"HTTP_FORWARDED": "for=127.0.0.1"},
            {"HTTP_X_FORWARDED_HOST": "127.0.0.1:8002"},
        ):
            self.assertEqual(views.status(self.request(**extra)).status_code, 404)
        request = self.request()
        request.user.pk = 9
        self.assertEqual(views.status(request).status_code, 404)
        self.mock_backend.connection_exists.assert_not_called()

    def test_anonymous_callback_never_redirects_to_login(self):
        request = self.request(path="/connections/google/callback/?code=private")
        request.user.is_authenticated = False
        response = views.callback(request)
        self.assertEqual(response.status_code, 404)
        self.assertNotIn("Location", response)
        self.assert_private(response)

    def test_start_requires_post_and_csrf(self):
        self.assertEqual(views.start(self.request()).status_code, 405)
        request = self.request("post")
        request._dont_enforce_csrf_checks = False
        response = views.start(request)
        self.assertEqual(response.status_code, 403)
        self.assert_private(response)
        self.mock_backend.load_client_id.assert_not_called()

    def test_callback_consumes_state_and_redirects_cleanly(self):
        response = views.start(self.request("post"))
        self.assertEqual(response.status_code, 302)
        state = parse_qs(urlsplit(response["Location"]).query)["state"][0]
        query = urlencode({"state": state, "code": "synthetic-private-code"})
        request = self.request(path="/connections/google/callback/?" + query)
        response = views.callback(request)
        self.assertEqual(response["Location"], views.STATUS_PATH)
        self.assertEqual(self.session["google_local_result"], "saved")
        self.mock_backend.exchange_and_store.assert_called_once()
        self.assertNotIn("synthetic-private-code", str(dict(self.session)))
        self.assert_private(response)
        views.callback(request)
        self.mock_backend.exchange_and_store.assert_called_once()
        self.assertEqual(self.session["google_local_result"], "failed")

    def test_provider_denial_is_sanitized(self):
        response = views.start(self.request("post"))
        state = parse_qs(urlsplit(response["Location"]).query)["state"][0]
        response = views.callback(
            self.request(
                path="/connections/google/callback/?"
                + urlencode({"state": state, "error": "private-error"})
            )
        )
        self.assertEqual(response["Location"], views.STATUS_PATH)
        self.mock_backend.exchange_and_store.assert_not_called()
        self.assertNotIn("private-error", str(dict(self.session)))

    def test_disconnect_requires_post_and_handles_failure(self):
        self.assertEqual(views.disconnect(self.request()).status_code, 405)
        self.mock_backend.disconnect.side_effect = (
            self.mock_backend.ConnectionUnavailable()
        )
        response = views.disconnect(self.request("post"))
        self.assertEqual(response["Location"], views.STATUS_PATH)
        self.assertEqual(self.session["google_local_result"], "failed")
        self.assert_private(response)
