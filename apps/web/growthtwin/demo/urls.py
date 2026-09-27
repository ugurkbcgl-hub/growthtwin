"""Routes for the synthetic Phase 0 demo."""

from django.urls import path

from growthtwin.demo import views

app_name = "demo"

urlpatterns = [
    path("profile/", views.profile_edit, name="profile-edit"),
]
