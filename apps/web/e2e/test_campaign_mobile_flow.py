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
                brief = page.locator("#campaign-brief")
                brief.evaluate("(field) => field.removeAttribute('required')")
                brief.fill("")
                page.get_by_role("button", name="Örnek kampanyayı gör").click()
                page.wait_for_load_state("domcontentloaded")
                self.assertEqual(brief.get_attribute("aria-invalid"), "true")
                brief_error_id = brief.get_attribute("aria-describedby")
                self.assertEqual(brief_error_id, f"{brief.get_attribute('id')}-error")
                self.assertTrue(page.locator(f"#{brief_error_id}").inner_text())
                self.assertEqual(
                    page.evaluate("document.activeElement.id"),
                    brief.get_attribute("id"),
                )

                brief.fill("Sentetik örnek: hafta sonu seramik atölyesi için tanıtım")
                page.get_by_text("Marka veya ürün bilgisi ekle").click()
                brand_context = page.locator("#brand-context")
                brand_context.evaluate("(field) => field.removeAttribute('maxlength')")
                brand_context.fill("Sentetik " * 40)
                page.get_by_role("button", name="Örnek kampanyayı gör").click()
                page.wait_for_load_state("domcontentloaded")
                self.assertIsNotNone(page.locator(".optional-context").get_attribute("open"))
                self.assertEqual(brand_context.get_attribute("aria-invalid"), "true")
                brand_error_id = brand_context.get_attribute("aria-describedby")
                self.assertEqual(
                    brand_error_id,
                    f"{brand_context.get_attribute('id')}-error",
                )
                self.assertTrue(page.locator(f"#{brand_error_id}").inner_text())
                self.assertEqual(
                    page.evaluate("document.activeElement.id"),
                    brand_context.get_attribute("id"),
                )

                brief.fill("Sentetik örnek: hafta sonu seramik atölyesi için tanıtım")
                brand_context.fill("Sentetik seramik atölyesi")
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

                variants = page.locator(".creative-variant")
                second_variant = variants.nth(1)
                second_summary = second_variant.locator("summary")
                second_summary.focus()
                page.keyboard.press("Enter")
                self.assertIsNotNone(second_variant.get_attribute("open"))
                self.assertEqual(
                    second_variant.get_by_label("Başlık").count(),
                    1,
                )

                first_headline = variants.nth(0).get_by_label("Başlık")
                first_headline.fill("Sentetik düzenlenmiş reklam başlığı")
                page.get_by_role("button", name="Metinleri kaydet").click()
                page.wait_for_url("**creative=saved")
                self.assertEqual(
                    page.get_by_role("status")
                    .filter(has_text="Metin değişikliklerin kaydedildi.")
                    .count(),
                    1,
                )
                self.assertEqual(
                    page.locator(".creative-variant")
                    .nth(0)
                    .get_by_label("Başlık")
                    .input_value(),
                    "Sentetik düzenlenmiş reklam başlığı",
                )

                third_variant = page.locator(".creative-variant").nth(2)
                page.evaluate(
                    """() => document
                        .querySelectorAll(".creative-variants-form [required], " +
                                          ".creative-variants-form [maxlength]")
                        .forEach((field) => {
                          field.removeAttribute("required");
                          field.removeAttribute("maxlength");
                        })"""
                )
                invalid_headline = third_variant.get_by_label("Başlık")
                invalid_headline.evaluate("(field) => { field.value = ''; }")
                page.get_by_role("button", name="Metinleri kaydet").click()
                page.wait_for_load_state("domcontentloaded")
                self.assertIsNotNone(third_variant.get_attribute("open"))
                self.assertEqual(invalid_headline.get_attribute("aria-invalid"), "true")
                error_id = invalid_headline.get_attribute("aria-describedby")
                self.assertEqual(
                    error_id,
                    f"{invalid_headline.get_attribute('id')}-error",
                )
                self.assertTrue(page.locator(f"#{error_id}").inner_text())
                self.assertEqual(
                    page.evaluate("document.activeElement.id"),
                    invalid_headline.get_attribute("id"),
                )

                page.get_by_role(
                    "button", name="Brief’ten yeni öneriler oluştur"
                ).click()
                page.wait_for_url("**creative=regenerated")
                self.assertEqual(
                    page.get_by_role("status")
                    .filter(has_text="Brief’inden yeni metin önerileri hazırlandı.")
                    .count(),
                    1,
                )

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
