"""Ownership and deletion tests for synthetic workspace records."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from growthtwin.modules.workspaces.models import Workspace


class WorkspaceOwnershipTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username="owner")
        self.other_user = user_model.objects.create_user(username="other")

    def test_workspace_is_owned_by_one_authenticated_user(self):
        workspace = Workspace.objects.create(owner=self.owner, name="Synthetic shop")

        self.assertEqual(workspace.owner, self.owner)
        self.assertEqual(self.owner.workspaces.get(), workspace)
        self.assertFalse(self.other_user.workspaces.exists())

    def test_owner_scoped_queryset_does_not_return_another_users_workspace(self):
        workspace = Workspace.objects.create(owner=self.owner, name="Synthetic shop")

        self.assertFalse(
            Workspace.objects.filter(owner=self.other_user, pk=workspace.pk).exists()
        )

    def test_deleting_owner_deletes_owned_workspaces(self):
        workspace = Workspace.objects.create(owner=self.owner, name="Synthetic shop")
        workspace_id = workspace.pk

        self.owner.delete()

        self.assertFalse(Workspace.objects.filter(pk=workspace_id).exists())
