"""Authenticated local campaign planning routes."""

from django.urls import path

from growthtwin.modules.campaigns import views

app_name = "campaigns"

urlpatterns = [
    path("", views.campaign_list, name="list"),
    path("new/", views.campaign_create, name="create"),
    path("<int:draft_id>/", views.campaign_detail, name="detail"),
    path("<int:draft_id>/report/", views.campaign_report, name="report"),
    path("<int:draft_id>/edit/", views.campaign_edit, name="edit"),
    path(
        "<int:draft_id>/creatives/generate/",
        views.campaign_generate_creatives,
        name="generate_creatives",
    ),
    path(
        "<int:draft_id>/creatives/preference/",
        views.campaign_select_preferred_creative,
        name="select_preferred_creative",
    ),
    path(
        "<int:draft_id>/creatives/edit/",
        views.campaign_edit_creative,
        name="edit_creative",
    ),
    path(
        "<int:draft_id>/creatives/restore/",
        views.campaign_restore_creative,
        name="restore_creative",
    ),
    path("<int:draft_id>/delete/", views.campaign_delete, name="delete"),
]
