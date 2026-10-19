"""Local Google authorization endpoints."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.status, name="google-local-status"),
    path("start/", views.start, name="google-local-start"),
    path("callback/", views.callback, name="google-local-callback"),
    path("disconnect/", views.disconnect, name="google-local-disconnect"),
    path("verify/", views.verify_test_account, name="google-local-verify"),
    path(
        "test-campaign/", views.test_campaign_action, name="google-local-test-campaign"
    ),
]
