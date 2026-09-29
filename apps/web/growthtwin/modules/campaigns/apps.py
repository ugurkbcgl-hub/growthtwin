"""Django app configuration for campaign planning records."""

from django.apps import AppConfig


class CampaignsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "growthtwin.modules.campaigns"
    label = "campaigns"
    verbose_name = "Campaigns"
