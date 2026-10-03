"""Operational views shared by the GrowthTwin web application."""

import os

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def health(request):
    """Report readiness only when the application can reach its database."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")

    return JsonResponse(
        {
            "status": "ok",
            "version": _deployed_revision(),
        }
    )


def _deployed_revision():
    """Prefer current Heroku build metadata; retain the legacy slug fallback."""

    for variable in ("HEROKU_BUILD_COMMIT", "HEROKU_SLUG_COMMIT"):
        revision = os.environ.get(variable, "").strip()
        if revision:
            return revision
    return "unknown"
