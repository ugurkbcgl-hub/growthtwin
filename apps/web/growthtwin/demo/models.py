"""Synthetic profile data used only to validate the Phase 0 workflow."""

from django.conf import settings
from django.db import models


class DemoProfile(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="demo_profile",
    )
    clinic_name = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    website = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.clinic_name or f"{self.owner.get_username()}'s demo profile"
