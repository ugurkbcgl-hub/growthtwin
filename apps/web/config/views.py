"""Operational views shared by the Phase 0 application."""

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
            "version": os.environ.get("HEROKU_SLUG_COMMIT", "unknown"),
        }
    )
