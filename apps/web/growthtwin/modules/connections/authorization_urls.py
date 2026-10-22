"""Synthetic session rehearsal, separate from Google endpoints."""

from django.urls import path

from . import authorization_views as views

app_name = "authorization_rehearsal"
urlpatterns = [
    path("<int:workspace_id>/", views.overview, name="overview"),
    path("<int:workspace_id>/start/", views.start, name="start"),
    path("<int:workspace_id>/recovery/", views.recovery, name="recovery"),
    path(
        "<int:workspace_id>/<uuid:connection_id>/<uuid:attempt_id>/recover/",
        views.recover,
        name="recover",
    ),
    path(
        "<int:workspace_id>/<uuid:connection_id>/<uuid:attempt_id>/",
        views.status,
        name="status",
    ),
    path(
        "<int:workspace_id>/<uuid:connection_id>/<uuid:attempt_id>/perform/",
        views.perform,
        name="perform",
    ),
]
