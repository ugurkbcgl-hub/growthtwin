"""Default-off scoped TEST endpoints, separate from legacy callbacks."""

from django.urls import path

from . import scoped_views as views

app_name = "scoped_candidate"
urlpatterns = [
    path("", views.overview, name="overview"),
    path("start/", views.start, name="start"),
    path("callback/", views.callback, name="callback"),
    path("callback", views.callback),
    path("retire/", views.retire, name="retire"),
]
