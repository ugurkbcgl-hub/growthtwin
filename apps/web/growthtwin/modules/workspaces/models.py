"""Synthetic workspace records owned by authenticated users."""

from django.conf import settings
from django.db import models


class Workspace(models.Model):
    """A future tenant boundary; current campaign drafts remain session-owned."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workspaces",
    )
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name", "pk")

    def __str__(self) -> str:
        return self.name
