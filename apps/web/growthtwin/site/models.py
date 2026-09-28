"""Session-scoped, synthetic campaign drafts for the local product prototype."""

import uuid

from django.contrib.sessions.models import Session
from django.db import models
from django.db.models import Q


class CampaignObjective(models.TextChoices):
    AWARENESS = "awareness", "Markamı daha çok kişiye duyurmak"
    WEBSITE_TRAFFIC = "traffic", "Web siteme ziyaretçi çekmek"
    LEADS = "leads", "Potansiyel müşteri bulmak"
    SALES = "sales", "Satış, randevu veya rezervasyon almak"
    LOCAL_VISITS = "local_visits", "Mağaza veya konum ziyareti sağlamak"


class CampaignDraft(models.Model):
    """A temporary campaign brief owned by one anonymous browser session."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Status(models.TextChoices):
        DRAFT = "draft", "Taslak"

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="campaign_drafts",
    )
    brief = models.CharField(max_length=280)
    brand_context = models.CharField(max_length=320, blank=True, default="")
    objective = models.CharField(
        max_length=20,
        choices=CampaignObjective.choices,
        blank=True,
        default="",
    )
    daily_limit = models.PositiveIntegerField()
    duration_days = models.PositiveSmallIntegerField()
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.CheckConstraint(
                condition=Q(daily_limit__gte=100) & Q(daily_limit__lte=100000),
                name="campaign_draft_daily_limit_range",
            ),
            models.CheckConstraint(
                condition=Q(duration_days__in=(7, 14, 30)),
                name="campaign_draft_duration_allowed",
            ),
            models.CheckConstraint(
                condition=Q(objective="") | Q(objective__in=CampaignObjective.values),
                name="campaign_draft_objective_allowed",
            ),
        ]

    @property
    def total_limit(self) -> int:
        return self.daily_limit * self.duration_days
