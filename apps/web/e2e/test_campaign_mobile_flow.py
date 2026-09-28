"""Browser checks for the mobile synthetic campaign journey."""

from django.test import LiveServerTestCase
from playwright.sync_api import sync_playwright


class CampaignMobileFlowBrowserTests(LiveServerTestCase):
    """Keep the first-visit brief, preview, and report usable on mobile."""

    def test_campaign_journey_fits_a_mobile_viewport(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 390, "height": 844})
                page.goto(self.live_server_url)

                self.assert_no_horizontal_overflow(page)
                page.locator("#campaign-brief").fill(
                    "Sentetik örnek: hafta sonu seramik atölyesi için tanıtım"
                )
                page.get_by_role("button", name="Örnek kampanyayı gör").click()
                page.wait_for_url("**campaign=*")
                self.assertEqual(page.locator("#step-count").inner_text(), "2 / 3")
                self.assert_no_horizontal_overflow(page)

                pause_button = page.get_by_role("button", name="Örnek akışı durdur")
                self.assertNotIn("pressed", pause_button.aria_snapshot())
                pause_button.click()
                resume_button = page.get_by_role(
                    "button", name="Örnek akışı devam ettir"
                )
                self.assertNotIn("pressed", resume_button.aria_snapshot())
                self.assertEqual(
                    page.locator("#flow-status").inner_text(),
                    "Örnek akış duraklatıldı. Gerçek kampanya yok.",
                )
                self.assertEqual(
                    page.locator("#flow-status").get_attribute("aria-live"),
                    "polite",
                )
                self.assert_no_horizontal_overflow(page)
                resume_button.click()

                page.get_by_role("button", name="Örnek rapor").click()
                self.assertEqual(page.locator("#step-count").inner_text(), "3 / 3")
                self.assert_no_horizontal_overflow(page)
            finally:
                browser.close()

    def assert_no_horizontal_overflow(self, page):
        dimensions = page.evaluate(
            "({viewport: window.innerWidth, document: document.documentElement.scrollWidth})"
        )
        self.assertEqual(dimensions["document"], dimensions["viewport"])
