"""Django app configuration for synthetic action-policy contracts."""

from django.apps import AppConfig


class ApprovalsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "growthtwin.modules.approvals"
    label = "approvals"
    verbose_name = "Approvals"
