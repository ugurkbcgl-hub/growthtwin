"""Routes for the public GrowthTwin product experience."""

from django.urls import path

from growthtwin.site import views

app_name = "site"

urlpatterns = [path("", views.home, name="home")]
