"""Project URL configuration for the Phase 0 demo."""

from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("demo/", include("growthtwin.demo.urls")),
]
