"""Browser coverage for the authenticated synthetic campaign workspace."""

import secrets

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from django.urls import reverse
from playwright.sync_api import sync_playwright

from growthtwin.modules.campaigns.models import WorkspaceCampaignDraft
from growthtwin.modules.workspaces.models import Workspace


class CampaignWorkspaceBrowserTests(LiveServerTestCase):
    """Verify the owner flow and tenant boundary in a real browser."""

    def setUp(self):
        user_model = get_user_model()
        self.owner_password = secrets.token_urlsafe(24)
        self.other_password = secrets.token_urlsafe(24)
        self.owner = user_model.objects.create_user(
            username=f"campaign-owner-{secrets.token_hex(4)}",
            password=self.owner_password,
        )
        self.other_user = user_model.objects.create_user(
            username=f"campaign-other-{secrets.token_hex(4)}",
            password=self.other_password,
        )
        self.workspace = Workspace.objects.create(
            owner=self.owner,
            name="Sentetik reklam çalışma alanı",
        )

    def test_owner_can_create_edit_and_delete_synthetic_campaign(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 390, "height": 844})
                page.goto(f"{self.live_server_url}{reverse('campaigns:list')}")
                page.locator("input[name='username']").fill(self.owner.username)
                page.locator("input[name='password']").fill(self.owner_password)
                page.get_by_role("button", name="Giriş yap").click()
                page.wait_for_url(f"**{reverse('campaigns:list')}")
                self.assert_no_horizontal_overflow(page)

                page.get_by_role("link", name="Yeni kampanya oluştur").click()
                page.locator("#id_workspace").select_option(str(self.workspace.pk))
                page.locator("#id_synthetic_confirmation").check()
                page.get_by_role(
                    "button", name="Sentetik örnekle taslağı hazırla"
                ).click()
                page.wait_for_url("**/workspace/campaigns/*/")
                draft_id = int(page.url.rstrip("/").rsplit("/", 1)[-1])
                self.assertIn(
                    "Önizleme · yayınlanmadı", page.locator("body").inner_text()
                )
                self.assertIn(
                    "Farklı reklam metinleri", page.locator("body").inner_text()
                )
                self.assertIn("Kısa tanıtım", page.locator("body").inner_text())
                page.get_by_role("button", name="Bu taslağı tercih et").nth(1).click()
                self.assertIn(
                    "Tercih yalnızca inceleme içindir",
                    page.locator("body").inner_text(),
                )
                self.assertEqual(
                    page.get_by_text("Tercih edilen taslak · sürüm 1").count(), 1
                )
                self.assert_no_horizontal_overflow(page)

                detail_url = reverse("campaigns:detail", args=[draft_id])
                page.get_by_role("link", name="Kampanya raporunu aç").click()
                page.wait_for_url(f"**{reverse('campaigns:report', args=[draft_id])}")
                self.assertIn(
                    "Rapor verisi henüz bağlı değil", page.locator("body").inner_text()
                )
                self.assertEqual(
                    page.get_by_text("Veri kaynağı bağlı değil").count(), 6
                )
                self.assertEqual(
                    page.get_by_text("Planlanan kampanya dönemi:", exact=False).count(),
                    6,
                )
                self.assert_no_horizontal_overflow(page)
                page.get_by_role("link", name="Kampanyaya dön").click()
                page.wait_for_url(f"**{detail_url}")
                page.get_by_role("link", name="Örnek bütçe ve süreyi düzenle").click()
                page.locator("#id_media_budget_minor").select_option("1000000")
                page.locator("#id_duration_days").select_option("30")
                page.locator("#id_synthetic_confirmation").check()
                page.get_by_role("button", name="Ayarları kaydet").click()
                page.wait_for_url(f"**{detail_url}")

                self.assertIn("10.000,00 TRY", page.locator("body").inner_text())
            finally:
                browser.close()

        draft = WorkspaceCampaignDraft.objects.get(pk=draft_id)
        self.assertEqual(draft.media_budget_minor, 1_000_000)
        self.assertEqual((draft.flight_end - draft.flight_start).days, 30)
        self.assertEqual(len(draft.creative_versions), 1)
        self.assertEqual(draft.preferred_creative_key, "audience-focused")
        self.assertEqual(draft.preferred_creative_version, 1)

    def test_owner_can_confirm_campaign_deletion(self):
        draft = WorkspaceCampaignDraft.objects.create(
            workspace=self.workspace,
            name="Sentetik silme örneği",
            brand_name="Başkent Ev Bakım (Sentetik)",
            brief="Sentetik servis örneği.",
            target_city="Ankara",
            destination_url="https://example.invalid/ev-bakim",
            media_budget_minor=500_000,
        )

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 390, "height": 844})
                page.goto(
                    f"{self.live_server_url}{reverse('campaigns:detail', args=[draft.pk])}"
                )
                page.locator("input[name='username']").fill(self.owner.username)
                page.locator("input[name='password']").fill(self.owner_password)
                page.get_by_role("button", name="Giriş yap").click()
                page.wait_for_url(f"**{reverse('campaigns:detail', args=[draft.pk])}")
                page.locator("input[name='confirm_delete']").check()
                page.get_by_role("button", name="Taslağı sil").click()
                page.wait_for_url(f"**{reverse('campaigns:list')}")
                self.assertIn(
                    "Henüz kampanya taslağın yok", page.locator("body").inner_text()
                )
                self.assert_no_horizontal_overflow(page)
            finally:
                browser.close()

        self.assertFalse(WorkspaceCampaignDraft.objects.filter(pk=draft.pk).exists())

    def test_other_user_sees_not_found_for_foreign_campaign(self):
        draft = WorkspaceCampaignDraft.objects.create(
            workspace=self.workspace,
            name="Sentetik owner sınırı örneği",
            brand_name="Başkent Ev Bakım (Sentetik)",
            brief="Sentetik servis örneği.",
            target_city="Ankara",
            destination_url="https://example.invalid/ev-bakim",
            media_budget_minor=500_000,
        )

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(f"{self.live_server_url}{reverse('login')}")
                page.locator("input[name='username']").fill(self.other_user.username)
                page.locator("input[name='password']").fill(self.other_password)
                page.get_by_role("button", name="Giriş yap").click()
                page.wait_for_url(f"**{reverse('demo:profile-edit')}")

                response = page.goto(
                    f"{self.live_server_url}{reverse('campaigns:detail', args=[draft.pk])}"
                )
                self.assertIsNotNone(response)
                self.assertEqual(response.status, 404)
            finally:
                browser.close()

    def assert_no_horizontal_overflow(self, page):
        dimensions = page.evaluate(
            "({viewport: window.innerWidth, document: document.documentElement.scrollWidth})"
        )
        self.assertEqual(dimensions["document"], dimensions["viewport"])
