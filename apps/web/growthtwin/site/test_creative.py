"""Focused checks for provider-free creative copy fallbacks."""

from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID

from django.test import RequestFactory, SimpleTestCase

from growthtwin.modules.content.creative import draft_creative_variants
from growthtwin.modules.content.planning import CampaignBrief
from growthtwin.site.forms import CampaignDraftForm
from growthtwin.site.views import render_campaign_home


class CreativeFallbackTests(SimpleTestCase):
    def make_brief(self, *, brand_context="", target_audience=""):
        return CampaignBrief(
            text="Hafta sonu seramik atölyesini tanıtmak istiyorum",
            objective="",
            objective_label="",
            target_audience=target_audience,
            brand_context=brand_context,
        )

    def test_missing_audience_keeps_brief_out_of_cta_copy(self):
        brief = self.make_brief()

        variants = draft_creative_variants(brief)

        audience_variant = next(
            variant for variant in variants if variant.key == "audience-focused"
        )
        self.assertEqual(audience_variant.body, brief.text)
        self.assertEqual(audience_variant.call_to_action, "Daha fazlasını keşfet")
        self.assertNotIn("Detayları incele.", audience_variant.body)

    def test_missing_brand_and_audience_do_not_add_product_claims(self):
        brief = self.make_brief()

        variants = draft_creative_variants(brief)

        for variant in variants:
            with self.subTest(variant=variant.key):
                self.assertNotIn("en iyi", variant.body.casefold())
                self.assertNotIn("ücretsiz", variant.body.casefold())
        info_variant = next(
            variant for variant in variants if variant.key == "information-focused"
        )
        self.assertEqual(info_variant.headline, "Daha fazla bilgi")
        self.assertEqual(info_variant.body, brief.text)

    def test_provided_audience_is_kept_in_audience_focused_variant(self):
        variants = draft_creative_variants(
            self.make_brief(target_audience="Hafta sonu etkinliği arayanlar")
        )

        audience_variant = next(
            variant for variant in variants if variant.key == "audience-focused"
        )
        self.assertTrue(
            audience_variant.body.startswith("Hafta sonu etkinliği arayanlar için:")
        )

    def test_brand_and_audience_do_not_hide_the_offer_from_copy(self):
        brief = CampaignBrief(
            text="Ekşi mayalı ekmeklerimizi tanıtmak istiyorum.",
            objective="",
            objective_label="",
            target_audience="Yakındaki çalışanlar",
            brand_context="Mahalle fırını",
        )

        variants = draft_creative_variants(brief)

        audience_variant = next(
            variant for variant in variants if variant.key == "audience-focused"
        )
        info_variant = next(
            variant for variant in variants if variant.key == "information-focused"
        )
        self.assertIn("Yakındaki çalışanlar için:", audience_variant.body)
        self.assertIn("Ekşi mayalı ekmeklerimizi", audience_variant.body)
        self.assertEqual(info_variant.body, brief.text)
        self.assertEqual(info_variant.headline, "Mahalle fırını hakkında")

    def test_copy_editor_explains_unmodified_brief_fallback(self):
        campaign = SimpleNamespace(
            brief="Yeni seramik atölyemi tanıtmak istiyorum",
            objective="",
            get_objective_display=lambda: "",
            target_audience="",
            brand_context="",
            daily_limit=750,
            duration_days=7,
            creative_variants=[],
            creative_source_hash="",
            pk=UUID("2f8697ba-ac40-43d3-878d-1470cc71f324"),
        )
        request = RequestFactory().get("/")
        request.session = SimpleNamespace(session_key=None)

        with patch("growthtwin.site.views.CampaignDraft.objects.none", return_value=[]):
            response = render_campaign_home(request, CampaignDraftForm(), campaign)

        self.assertContains(response, "brief’in aynen korunabilir")
        self.assertContains(response, "yayına almadan önce düzenle")
        self.assertContains(response, "bilgileri doğrula")
