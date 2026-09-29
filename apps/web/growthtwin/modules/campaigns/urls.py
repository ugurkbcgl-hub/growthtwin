"""Authenticated local campaign planning routes."""

from django.urls import path

from growthtwin.modules.campaigns import views

app_name = "campaigns"

urlpatterns = [
    path("", views.campaign_list, name="list"),
    path("new/", views.campaign_create, name="create"),
    path("<int:draft_id>/", views.campaign_detail, name="detail"),
]
