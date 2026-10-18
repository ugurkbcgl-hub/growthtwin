"""Form origin must remain available to CSRF checks; callback stays private."""

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from .middleware import LocalOAuthHeadersMiddleware


class LocalOAuthHeadersTests(SimpleTestCase):
    def test_form_preserves_same_origin_callback_suppresses_referrer(self):
        middleware = LocalOAuthHeadersMiddleware(lambda request: HttpResponse())
        for path, policy in (
            ("/connections/google/", "same-origin"),
            ("/connections/google/callback/?code=fabricated", "no-referrer"),
            ("/connections/google/start/", "no-referrer"),
        ):
            response = middleware(RequestFactory().get(path))
            self.assertEqual(response["Referrer-Policy"], policy)
            self.assertIn("no-store", response["Cache-Control"])
