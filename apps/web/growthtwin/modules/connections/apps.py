"""Connection metadata; synthetic lifecycle storage has no provider executor."""

from django.apps import AppConfig


class ConnectionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "growthtwin.modules.connections"
    label = "connections"
