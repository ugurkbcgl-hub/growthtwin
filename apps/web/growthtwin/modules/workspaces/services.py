"""Owner-scoped workspace application queries."""

from django.core.exceptions import PermissionDenied

from growthtwin.modules.workspaces.models import Workspace


def get_workspace_for_owner(*, owner, workspace_id):
    """Fetch a workspace only when the authenticated user owns it."""

    if not getattr(owner, "is_authenticated", False):
        raise PermissionDenied("An authenticated workspace owner is required.")
    return Workspace.objects.get(pk=workspace_id, owner=owner)
