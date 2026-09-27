"""Tests for application operations endpoints."""

import os
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class HealthEndpointTests(TestCase):
    def test_health_reports_ready_database_and_deployed_revision(self):
        with patch.dict(os.environ, {"HEROKU_SLUG_COMMIT": "synthetic-revision"}):
            response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok", "version": "synthetic-revision"},
        )

    def test_health_rejects_non_get_requests(self):
        response = self.client.post(reverse("health"))

        self.assertEqual(response.status_code, 405)
