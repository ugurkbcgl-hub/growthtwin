"""Django app configuration for workspace ownership."""

from django.apps import AppConfig


class WorkspacesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "growthtwin.modules.workspaces"
    label = "workspaces"
    verbose_name = "Workspaces"
