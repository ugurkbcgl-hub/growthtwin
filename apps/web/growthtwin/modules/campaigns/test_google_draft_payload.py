"""Selected-copy mapping keeps source changes visible and snapshots immutable."""

import hashlib
import json
from dataclasses import FrozenInstanceError
from datetime import date

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from growthtwin.modules.campaigns.google_draft_payload import build_draft_package
from growthtwin.modules.campaigns.models import WorkspaceCampaignDraft
from growthtwin.modules.campaigns.services import creative_source_hash_for_draft


class GoogleDraftPackageTests(SimpleTestCase):
    def setUp(self):
        self.draft = WorkspaceCampaignDraft(
            pk=17,
            workspace_id=8,
            name="Sentetik deneme",
            brand_name="Örnek Atölye",
            brief="Sentetik ürünleri ve hizmetleri web sitesinde inceleyin.",
            target_city="Ankara",
            destination_url="https://example.invalid/urun?ref=ilk",
            media_budget_minor=500000,
            currency="TRY",
            flight_start=date(2026, 11, 1),
            flight_end=date(2026, 11, 15),
            preferred_creative_version=1,
            preferred_creative_key="first",
        )
        self.variant = {
            "key": "first",
            "headline": "Size özel sentetik ürünler ve hizmetler",
            "body": "Sentetik açıklama " * 10,
            "call_to_action": "Ürünleri inceleyin",
            "claims": ["Synthetic only"],
        }
        self.draft.creative_versions = [
            {
                "version": 1,
                "source_hash": creative_source_hash_for_draft(self.draft),
                "variants": [self.variant],
            }
        ]

    def test_maps_selected_text_with_visible_shortening_and_preserved_url(self):
        package = build_draft_package(self.draft)
        payload = json.loads(package.payload_json)
        google = payload["google"]
        self.assertEqual(google["final_url"], self.draft.destination_url)
        self.assertEqual(google["status"], "PAUSED")
        for field, count, limit in (("headlines", 3, 30), ("descriptions", 2, 90)):
            self.assertEqual(len(google[field]), count)
            self.assertEqual(len({text.casefold() for text in google[field]}), count)
            self.assertTrue(all(0 < len(text) <= limit for text in google[field]))
        self.assertEqual(payload["source"]["selected"], self.variant)
        transformations = payload["transformations"]
        self.assertTrue(transformations[0]["shortened"])
        self.assertEqual(transformations[0]["original"], self.variant["headline"])
        self.assertEqual(transformations[0]["mapped"], google["headlines"][0])
        self.assertFalse(payload["validation"]["google_approval"])
        self.assertFalse(payload["validation"]["publication_enabled"])

    def test_missing_or_stale_preference_is_rejected(self):
        for field, changed in (
            ("preferred_creative_key", ""),
            ("preferred_creative_version", 2),
            ("brand_name", "Değişen kaynak"),
        ):
            original = getattr(self.draft, field)
            with self.subTest(field=field), self.assertRaises(ValidationError):
                setattr(self.draft, field, changed)
                build_draft_package(self.draft)
            setattr(self.draft, field, original)

    def test_every_plan_change_changes_fingerprint(self):
        original = build_draft_package(self.draft).fingerprint
        for field, changed in (
            ("media_budget_minor", 700000),
            ("destination_url", "https://example.invalid/other"),
            ("flight_end", date(2026, 11, 20)),
            ("name", "Başka sentetik plan"),
        ):
            before = getattr(self.draft, field)
            setattr(self.draft, field, changed)
            with self.subTest(field=field):
                self.assertNotEqual(
                    build_draft_package(self.draft).fingerprint, original
                )
            setattr(self.draft, field, before)
        self.variant["claims"].append("A new selected attribute")
        self.assertNotEqual(build_draft_package(self.draft).fingerprint, original)

    def test_snapshot_is_canonical_stable_and_immutable(self):
        package = build_draft_package(self.draft)
        self.assertEqual(package, build_draft_package(self.draft))
        self.assertEqual(
            package.fingerprint,
            hashlib.sha256(package.payload_json.encode("utf-8")).hexdigest(),
        )
        self.variant["headline"] = "Sonradan değişti"
        self.assertNotIn("Sonradan değişti", package.payload_json)
        with self.assertRaises(FrozenInstanceError):
            package.payload_json = "changed"

    def test_incomplete_or_unsupported_plans_are_rejected(self):
        for field, changed in (
            ("channel", "other"),
            ("currency", "USD"),
            ("flight_end", date(2026, 10, 1)),
            ("flight_start", None),
            ("media_budget_minor", 0),
            ("destination_url", "javascript:alert(1)"),
        ):
            original = getattr(self.draft, field)
            setattr(self.draft, field, changed)
            with self.subTest(field=field), self.assertRaises(ValidationError):
                build_draft_package(self.draft)
            setattr(self.draft, field, original)

    def test_duplicate_selected_assets_use_explicit_plan_fallbacks(self):
        self.variant.update(headline="Aynı", body="Aynı", call_to_action="Aynı")
        payload = json.loads(build_draft_package(self.draft).payload_json)
        self.assertEqual(len(payload["google"]["headlines"]), 3)
        self.assertEqual(len(payload["google"]["descriptions"]), 2)
        self.assertTrue(
            any(t["source"].startswith("plan.") for t in payload["transformations"])
        )
