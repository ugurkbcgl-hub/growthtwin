"""Focused authenticated synthetic brand screen boundaries."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from growthtwin.modules.workspaces.brand_views import _foreground
from growthtwin.modules.workspaces.models import Brand, Workspace
from growthtwin.modules.workspaces.services import create_brand_for_owner


@override_settings(
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        }
    }
)
class BrandViewTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="brand-owner")
        self.other = get_user_model().objects.create_user(username="brand-other")
        self.workspace = Workspace.objects.create(owner=self.owner, name="Örnek alan")
        self.brand = create_brand_for_owner(
            owner=self.owner, workspace_id=self.workspace.pk, fixture="product"
        )
        self.client.force_login(self.owner)

    def payload(self):
        return {
            "expected_version": 1,
            "primary_color": "#245C48",
            "secondary_color": "#F4E8D2",
            "tone": "energetic",
            "tagline_key": "daily_detail",
        }

    def test_login_required(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("brands:list")).status_code, 302)

    def test_owned_list_and_detail(self):
        self.assertContains(self.client.get(reverse("brands:list")), self.brand.name)
        self.assertContains(
            self.client.get(reverse("brands:detail", args=[self.brand.pk])),
            "Kimlik geçmişi",
        )

    def test_foreign_brand_hidden_on_get_and_post(self):
        self.client.force_login(self.other)
        for route in ("brands:detail", "brands:edit"):
            self.assertEqual(
                self.client.get(reverse(route, args=[self.brand.pk])).status_code, 404
            )
        self.assertEqual(
            self.client.post(
                reverse("brands:edit", args=[self.brand.pk]), self.payload()
            ).status_code,
            404,
        )
        self.assertNotContains(self.client.get(reverse("brands:list")), self.brand.name)

    def test_create_two_distinct_brands_and_no_duplicate(self):
        for fixture in ("service", "product"):
            self.assertEqual(
                self.client.post(
                    reverse("brands:create"),
                    {"workspace": self.workspace.pk, "fixture": fixture},
                ).status_code,
                302,
            )
        self.assertEqual(Brand.objects.filter(workspace=self.workspace).count(), 2)

    def test_foreign_workspace_rejected(self):
        other_workspace = Workspace.objects.create(owner=self.other, name="Other")
        response = self.client.post(
            reverse("brands:create"),
            {"workspace": other_workspace.pk, "fixture": "service"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Brand.objects.filter(workspace=other_workspace).exists())

    def test_edit_preserves_history_and_stale_form_conflicts(self):
        url = reverse("brands:edit", args=[self.brand.pk])
        self.assertEqual(self.client.post(url, self.payload()).status_code, 302)
        self.assertEqual(self.client.post(url, self.payload()).status_code, 409)
        self.brand.refresh_from_db()
        self.assertEqual(self.brand.current_version, 2)
        self.assertEqual(self.brand.identities.count(), 2)

    def test_invalid_choices_and_color_injection_rejected(self):
        payload = self.payload()
        payload["primary_color"] = "red; background:url(https://invalid.example)"
        payload["tagline_key"] = "private-real-advertiser-text"
        self.assertEqual(
            self.client.post(
                reverse("brands:edit", args=[self.brand.pk]), payload
            ).status_code,
            200,
        )
        self.assertEqual(self.brand.identities.count(), 1)

    def test_csrf_required(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(
            client.post(
                reverse("brands:edit", args=[self.brand.pk]), self.payload()
            ).status_code,
            403,
        )
        self.assertEqual(client.post(reverse("brands:prepare")).status_code, 403)

    def test_prepare_is_post_only_owner_scoped_and_idempotent(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("brands:prepare")).status_code, 405)
        self.client.get(reverse("brands:list"))
        self.assertFalse(Workspace.objects.filter(owner=self.other).exists())
        for _ in range(2):
            self.assertEqual(
                self.client.post(
                    reverse("brands:prepare"), {"owner": self.owner.pk}
                ).status_code,
                302,
            )
        self.assertEqual(Workspace.objects.filter(owner=self.other).count(), 1)

    def test_get_edit_does_not_write_or_switch_global_brand(self):
        self.client.get(reverse("brands:edit", args=[self.brand.pk]))
        self.assertEqual(self.brand.identities.count(), 1)
        self.assertNotIn("brand_id", self.client.session)

    def test_archived_brand_hidden_and_cannot_recreate(self):
        Brand.objects.filter(pk=self.brand.pk).update(is_archived=True)
        self.assertNotContains(self.client.get(reverse("brands:list")), self.brand.name)
        response = self.client.post(
            reverse("brands:create"),
            {"workspace": self.workspace.pk, "fixture": "product"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bu örnek şu anda eklenemiyor")

    def test_owner_scope_race_becomes_not_found(self):
        with patch(
            "growthtwin.modules.workspaces.brand_views.create_brand_for_owner",
            side_effect=Workspace.DoesNotExist,
        ):
            response = self.client.post(
                reverse("brands:create"),
                {"workspace": self.workspace.pk, "fixture": "service"},
            )
            self.assertEqual(response.status_code, 404)
        with patch(
            "growthtwin.modules.workspaces.brand_views.update_brand_identity_for_owner",
            side_effect=Brand.DoesNotExist,
        ):
            self.assertEqual(
                self.client.post(
                    reverse("brands:edit", args=[self.brand.pk]), self.payload()
                ).status_code,
                404,
            )

    def test_preview_foreground_adapts_to_dark_and_light_palette(self):
        self.assertEqual(_foreground("#244c3b"), "#FFFFFF")
        self.assertEqual(_foreground("#F4E8D2"), "#000000")
