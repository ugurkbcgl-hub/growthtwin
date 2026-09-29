"""Django app configuration for provider-independent asset contracts."""

from django.apps import AppConfig


class AssetsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "growthtwin.modules.assets"
    label = "assets"
    verbose_name = "Assets"
