"""Owner-scoped campaign draft application operations."""

from django.core.exceptions import ValidationError

from growthtwin.modules.campaigns.models import WorkspaceCampaignDraft
from growthtwin.modules.campaigns.synthetic_rules import (
    ALLOWED_SYNTHETIC_BUDGETS_MINOR,
    ALLOWED_SYNTHETIC_DURATIONS_DAYS,
)
from growthtwin.modules.workspaces.services import get_workspace_for_owner


def get_campaign_draft_for_owner(*, owner, draft_id):
    """Fetch a draft only through the authenticated workspace owner."""

    return WorkspaceCampaignDraft.objects.owned_by(owner).get(pk=draft_id)


def create_campaign_draft_for_owner(*, owner, workspace_id, **values):
    """Create a draft only in a workspace owned by the supplied user."""

    workspace = get_workspace_for_owner(owner=owner, workspace_id=workspace_id)
    draft = WorkspaceCampaignDraft(workspace=workspace, **values)
    draft.full_clean()
    draft.save()
    return draft


def update_campaign_draft_for_owner(
    *, owner, draft_id, media_budget_minor, flight_start, flight_end
):
    """Update only bounded campaign settings through the owning user."""

    draft = WorkspaceCampaignDraft.objects.owned_by(owner).get(pk=draft_id)
    if media_budget_minor not in ALLOWED_SYNTHETIC_BUDGETS_MINOR:
        raise ValidationError(
            {"media_budget_minor": "Bilinmeyen sentetik bütçe seçeneği."}
        )
    if flight_start is None or flight_end is None:
        raise ValidationError({"flight_end": "Sentetik kampanya süresi gerekli."})
    duration = (flight_end - flight_start).days
    if duration not in ALLOWED_SYNTHETIC_DURATIONS_DAYS:
        raise ValidationError({"flight_end": "Bilinmeyen sentetik süre seçeneği."})

    draft.media_budget_minor = media_budget_minor
    draft.flight_start = flight_start
    draft.flight_end = flight_end
    draft.full_clean()
    draft.save(
        update_fields=("media_budget_minor", "flight_start", "flight_end", "updated_at")
    )
    return draft
