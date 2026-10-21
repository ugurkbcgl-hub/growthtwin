"""Opt-in synthetic owner journey, separate from Google connection endpoints."""

from django.urls import path

from . import lifecycle_views

app_name = "closure"

urlpatterns = [
    path("", lifecycle_views.overview, name="overview"),
    path("<int:workspace_id>/start/", lifecycle_views.start, name="start"),
    path(
        "<int:workspace_id>/<uuid:request_id>/", lifecycle_views.status, name="status"
    ),
]
