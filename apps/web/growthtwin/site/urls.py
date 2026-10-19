"""Routes for the public GrowthTwin product experience."""

from django.urls import path

from growthtwin.site import views
from growthtwin.site.information import information_page
from growthtwin.site.lifecycle_preview import lifecycle_preview

app_name = "site"

urlpatterns = [
    path("", views.home, name="home"),
    path("kontrol-onizleme/", lifecycle_preview, name="lifecycle-preview"),
    path("iletisim/", information_page, {"page_key": "contact"}, name="contact"),
    path("gizlilik/", information_page, {"page_key": "privacy"}, name="privacy"),
    path(
        "kullanim-kosullari/",
        information_page,
        {"page_key": "terms"},
        name="terms",
    ),
    path(
        "drafts/<uuid:campaign_id>/delete/",
        views.delete_campaign,
        name="delete-campaign",
    ),
    path(
        "drafts/<uuid:campaign_id>/creatives/",
        views.save_creatives,
        name="save-creatives",
    ),
]
