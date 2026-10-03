"""Tests for application operations endpoints."""

import os
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class HealthEndpointTests(TestCase):
    def test_health_prefers_current_build_revision(self):
        with patch.dict(
            os.environ,
            {
                "HEROKU_BUILD_COMMIT": "new-synthetic-revision",
                "HEROKU_SLUG_COMMIT": "old-synthetic-revision",
            },
        ):
            response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok", "version": "new-synthetic-revision"},
        )

    def test_health_falls_back_to_legacy_slug_revision(self):
        with patch.dict(
            os.environ,
            {
                "HEROKU_BUILD_COMMIT": "",
                "HEROKU_SLUG_COMMIT": "legacy-synthetic-revision",
            },
        ):
            response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok", "version": "legacy-synthetic-revision"},
        )

    def test_health_reports_unknown_when_revision_metadata_is_absent(self):
        with patch.dict(
            os.environ,
            {"HEROKU_BUILD_COMMIT": "", "HEROKU_SLUG_COMMIT": ""},
        ):
            response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "version": "unknown"})

    def test_health_rejects_non_get_requests(self):
        response = self.client.post(reverse("health"))

        self.assertEqual(response.status_code, 405)
