"""Synthetic, workspace-owned campaign drafts."""

from django.core.validators import MinValueValidator
from django.db import models

from growthtwin.modules.workspaces.models import Workspace


class WorkspaceCampaignDraftQuerySet(models.QuerySet):
    """Query helpers that make workspace ownership explicit at call sites."""

    def owned_by(self, user):
        return self.filter(workspace__owner=user)


class WorkspaceCampaignDraft(models.Model):
    """A locally planned campaign, separate from anonymous prototype drafts."""

    class Objective(models.TextChoices):
        LEAD_GENERATION = "lead_generation", "Lead generation"

    class Channel(models.TextChoices):
        GOOGLE_SEARCH = "google_search", "Google Search"

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="campaign_drafts",
    )
    name = models.CharField(max_length=120)
    brand_name = models.CharField(max_length=120, blank=True, default="")
    objective = models.CharField(
        max_length=32,
        choices=Objective.choices,
        default=Objective.LEAD_GENERATION,
    )
    channel = models.CharField(
        max_length=32,
        choices=Channel.choices,
        default=Channel.GOOGLE_SEARCH,
    )
    brief = models.TextField(max_length=4000)
    target_city = models.CharField(max_length=100)
    destination_url = models.URLField(max_length=500, blank=True)
    creative_versions = models.JSONField(blank=True, default=list)
    media_budget_minor = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Integer minor units; independent of GrowthTwin fees and credits.",
    )
    currency = models.CharField(max_length=3, default="TRY")
    flight_start = models.DateField(null=True, blank=True)
    flight_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WorkspaceCampaignDraftQuerySet.as_manager()

    class Meta:
        ordering = ("-updated_at", "pk")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(media_budget_minor__gt=0),
                name="campaign_draft_positive_media_budget",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(flight_start__isnull=True)
                    | models.Q(flight_end__isnull=True)
                    | models.Q(flight_end__gte=models.F("flight_start"))
                ),
                name="campaign_draft_flight_dates_ordered",
            ),
        ]
