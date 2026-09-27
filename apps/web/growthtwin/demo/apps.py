"""Configuration for the Phase 0 demonstration app."""

from django.apps import AppConfig


class DemoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "growthtwin.demo"
    verbose_name = "Phase 0 demo"
