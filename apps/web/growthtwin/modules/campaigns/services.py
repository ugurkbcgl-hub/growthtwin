"""Owner-scoped campaign draft application operations."""

from growthtwin.modules.campaigns.models import WorkspaceCampaignDraft
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
