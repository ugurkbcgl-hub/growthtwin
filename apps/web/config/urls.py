"""Project URL configuration for the public site and local workspace flows."""

from django.contrib.auth import views as auth_views
from django.urls import include, path

from config.views import health

urlpatterns = [
    path("health/", health, name="health"),
    path("", include("growthtwin.site.urls")),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("demo/", include("growthtwin.demo.urls")),
    path("workspace/campaigns/", include("growthtwin.modules.campaigns.urls")),
]
