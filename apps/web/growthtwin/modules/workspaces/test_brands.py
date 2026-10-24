"""Synthetic brand ownership, revision safety and competing-writer checks."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import close_old_connections
from django.test import TestCase, TransactionTestCase, skipUnlessDBFeature

from growthtwin.modules.campaigns.models import WorkspaceCampaignDraft
from growthtwin.modules.workspaces.models import (
    SYNTHETIC_BRAND_PRESETS,
    Brand,
    BrandIdentity,
    Workspace,
)
from growthtwin.modules.workspaces.services import (
    create_brand_for_owner,
    get_brand_for_owner,
    list_brands_for_owner,
    update_brand_identity_for_owner,
)


def changed_identity(owner, brand, **overrides):
    values = {
        "owner": owner,
        "brand_id": brand.pk,
        "expected_version": brand.current_version,
        "primary_color": "#183a35",
        "secondary_color": "#eeeeee",
        "tone": "energetic",
        "tagline_key": SYNTHETIC_BRAND_PRESETS[brand.fixture]["default_tagline"],
    }
    values.update(overrides)
    return update_brand_identity_for_owner(**values)


class SyntheticBrandTests(TestCase):
    def setUp(self):
        users = get_user_model()
        self.owner = users.objects.create_user(username="brand-owner")
        self.other = users.objects.create_user(username="brand-other")
        self.workspace = Workspace.objects.create(owner=self.owner, name="Örnek alan")
        self.other_workspace = Workspace.objects.create(
            owner=self.other, name="Başka alan"
        )

    def create(self, fixture="product"):
        return create_brand_for_owner(
            owner=self.owner, workspace_id=self.workspace.pk, fixture=fixture
        )

    def test_fixed_creation_is_idempotent_and_preserves_changed_identity(self):
        brand = self.create()
        initial = brand.current_identity
        self.assertEqual("product:logo:v1", initial.logo_key)
        self.assertEqual("Gününe küçük bir güzellik.", initial.tagline)
        changed_identity(self.owner, brand)
        repeated = self.create()
        self.assertEqual(brand.pk, repeated.pk)
        self.assertEqual(2, repeated.current_version)
        self.assertEqual("#183a35", repeated.current_identity.primary_color)
        self.assertEqual(1, Brand.objects.count())
        self.assertEqual(2, BrandIdentity.objects.count())

    def test_two_examples_are_independent_and_do_not_create_campaigns(self):
        product = self.create()
        service = self.create("service")
        self.assertNotEqual(product.pk, service.pk)
        self.assertEqual("service:logo:v1", service.current_identity.logo_key)
        self.assertIn("Ankara", service.synthetic_facts[0])
        self.assertEqual(
            2,
            list_brands_for_owner(
                owner=self.owner, workspace_id=self.workspace.pk
            ).count(),
        )
        self.assertEqual(0, WorkspaceCampaignDraft.objects.count())

    def test_same_example_can_exist_in_two_explicit_owned_workspaces(self):
        first = self.create()
        another = Workspace.objects.create(owner=self.owner, name="İkinci alan")
        second = create_brand_for_owner(
            owner=self.owner, workspace_id=another.pk, fixture="product"
        )
        self.assertNotEqual(first.pk, second.pk)
        self.assertEqual(
            [first],
            list(
                list_brands_for_owner(owner=self.owner, workspace_id=self.workspace.pk)
            ),
        )

    def test_foreign_owner_cannot_read_update_list_or_create(self):
        brand = self.create()
        with self.assertRaises(Brand.DoesNotExist):
            get_brand_for_owner(owner=self.other, brand_id=brand.pk)
        with self.assertRaises(Brand.DoesNotExist):
            changed_identity(self.other, brand)
        with self.assertRaises(Workspace.DoesNotExist):
            list_brands_for_owner(owner=self.other, workspace_id=self.workspace.pk)
        with self.assertRaises(Workspace.DoesNotExist):
            create_brand_for_owner(
                owner=self.other, workspace_id=self.workspace.pk, fixture="service"
            )
        self.assertEqual(1, BrandIdentity.objects.count())

    def test_anonymous_owner_is_denied_before_record_access(self):
        brand = self.create()
        for call in (
            lambda: get_brand_for_owner(owner=AnonymousUser(), brand_id=brand.pk),
            lambda: create_brand_for_owner(
                owner=AnonymousUser(), workspace_id=self.workspace.pk, fixture="product"
            ),
            lambda: list_brands_for_owner(
                owner=AnonymousUser(), workspace_id=self.workspace.pk
            ),
            lambda: changed_identity(AnonymousUser(), brand),
        ):
            with self.assertRaises(PermissionDenied):
                call()

    def test_update_appends_snapshot_and_stale_write_is_rejected(self):
        brand = self.create()
        initial = brand.current_identity
        new = changed_identity(
            self.owner, brand, primary_color="#AABBCC", tagline_key="daily_detail"
        )
        initial.refresh_from_db()
        self.assertEqual("#244c3b", initial.primary_color)
        self.assertEqual("small_beauty", initial.tagline_key)
        self.assertEqual("#aabbcc", new.primary_color)
        self.assertEqual(2, new.version)
        with self.assertRaises(ValidationError) as raised:
            changed_identity(self.owner, brand)
        self.assertEqual("stale_brand_version", raised.exception.code)
        self.assertEqual(2, brand.identities.count())

    def test_identical_current_update_does_not_create_a_revision(self):
        brand = self.create()
        identity = brand.current_identity
        repeated = changed_identity(
            self.owner,
            brand,
            primary_color=identity.primary_color,
            secondary_color=identity.secondary_color,
            tone=identity.tone,
            tagline_key=identity.tagline_key,
        )
        self.assertEqual(identity.pk, repeated.pk)
        self.assertEqual(1, brand.identities.count())

    def test_tagline_snapshot_survives_later_preset_copy_changes(self):
        brand = self.create()
        initial = brand.current_identity
        original_text = initial.tagline
        with patch.dict(
            SYNTHETIC_BRAND_PRESETS["product"]["taglines"],
            {"small_beauty": "Sonraki sentetik metin örneği."},
        ):
            initial.refresh_from_db()
            self.assertEqual(original_text, initial.tagline)
            self.assertEqual(original_text, initial.tagline_text)
            new = changed_identity(self.owner, brand)
            self.assertEqual("Sonraki sentetik metin örneği.", new.tagline)
            initial.refresh_from_db()
            self.assertEqual(original_text, initial.tagline)

    def test_malformed_or_cross_fixture_values_leave_history_unchanged(self):
        brand = self.create()
        for values in (
            {"expected_version": True},
            {"expected_version": "1"},
            {"primary_color": ["#ffffff"]},
            {"primary_color": "red"},
            {"secondary_color": "#ffffff\n"},
            {"tone": "customer supplied"},
            {"tagline_key": "city_care"},
            {"tagline_key": "<script>"},
        ):
            with self.subTest(values=values), self.assertRaises(ValidationError):
                changed_identity(self.owner, brand, **values)
        brand.refresh_from_db()
        self.assertEqual(1, brand.current_version)
        self.assertEqual(1, brand.identities.count())
        for fixture in ([], "real-customer"):
            with self.assertRaises(ValidationError):
                self.create(fixture)

    def test_model_and_queryset_mutation_cannot_edit_prior_snapshot(self):
        brand = self.create()
        initial = brand.current_identity
        initial.primary_color = "#ffffff"
        with self.assertRaises(ValidationError):
            initial.save()
        with self.assertRaises(ValidationError):
            BrandIdentity.objects.filter(pk=initial.pk).update(primary_color="#ffffff")
        with self.assertRaises(ValidationError):
            initial.delete()
        with self.assertRaises(ValidationError):
            BrandIdentity.objects.filter(pk=initial.pk).delete()
        replacement = BrandIdentity(
            pk=initial.pk,
            brand=brand,
            version=2,
            primary_color="#ffffff",
            secondary_color="#eeeeee",
            tone="calm",
            tagline_key="small_beauty",
            logo_key="product:logo:v1",
        )
        with self.assertRaises(ValidationError):
            replacement.save()
        initial.refresh_from_db()
        self.assertEqual("#244c3b", initial.primary_color)

    def test_failed_revision_creation_rolls_back_pointer(self):
        brand = self.create()
        with patch.object(
            BrandIdentity.objects,
            "create",
            side_effect=ValidationError("synthetic failure"),
        ):
            with self.assertRaises(ValidationError):
                changed_identity(self.owner, brand)
        brand.refresh_from_db()
        self.assertEqual(1, brand.current_version)
        self.assertEqual(1, brand.identities.count())

    def test_archived_example_cannot_be_recreated_or_modified(self):
        brand = self.create()
        Brand.objects.filter(pk=brand.pk).update(is_archived=True)
        with self.assertRaises(ValidationError):
            self.create()
        with self.assertRaises(Brand.DoesNotExist):
            changed_identity(self.owner, brand)
        self.assertFalse(
            list_brands_for_owner(
                owner=self.owner, workspace_id=self.workspace.pk
            ).exists()
        )


@skipUnlessDBFeature("has_select_for_update")
class SyntheticBrandConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="brand-race-owner")
        self.workspace = Workspace.objects.create(owner=self.owner, name="Yarış örneği")

    def run_together(self, operation):
        barrier = Barrier(2)
        owner_id = self.owner.pk

        def call():
            close_old_connections()
            try:
                owner = get_user_model().objects.get(pk=owner_id)
                barrier.wait(timeout=10)
                return operation(owner)
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(call) for _ in range(2)]
            return [future.result(timeout=20) for future in futures]

    def test_competing_creates_return_one_brand_and_identity(self):
        result = self.run_together(
            lambda owner: (
                create_brand_for_owner(
                    owner=owner, workspace_id=self.workspace.pk, fixture="product"
                ).pk
            )
        )
        self.assertEqual(result[0], result[1])
        self.assertEqual(1, Brand.objects.count())
        self.assertEqual(1, BrandIdentity.objects.count())

    def test_competing_edits_have_one_winner_and_one_stale_revision(self):
        brand = create_brand_for_owner(
            owner=self.owner, workspace_id=self.workspace.pk, fixture="product"
        )

        def edit(owner):
            try:
                return changed_identity(owner, brand).version
            except ValidationError as error:
                return error.code

        result = self.run_together(edit)
        self.assertCountEqual([2, "stale_brand_version"], result)
        self.assertEqual(2, BrandIdentity.objects.count())
        brand.refresh_from_db()
        self.assertEqual(2, brand.current_version)
