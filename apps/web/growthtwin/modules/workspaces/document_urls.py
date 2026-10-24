"""Explicit brand and UUID document scopes; no global selection."""

from django.urls import path

from growthtwin.modules.workspaces import document_views

app_name = "brand_documents"
urlpatterns = [
    path("create/", document_views.document_create, name="create"),
    path("<uuid:document_id>/", document_views.document_detail, name="detail"),
    path(
        "<uuid:document_id>/download/",
        document_views.document_download,
        name="download",
    ),
]
