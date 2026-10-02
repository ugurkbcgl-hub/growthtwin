"""Browser checks for the mobile synthetic campaign journey."""

from django.test import LiveServerTestCase
from playwright.sync_api import sync_playwright


class CampaignMobileFlowBrowserTests(LiveServerTestCase):
    """Keep the fixed-sample preview and report usable on mobile."""

    def test_regeneration_discloses_replacing_edited_copy(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 390, "height": 844})
                page.goto(self.live_server_url)
                page.get_by_role("button", name="Örnek kampanyayı gör").click()
                page.wait_for_url("**campaign=*#kampanya-denemesi")

                headline = page.locator(".creative-variant").first.get_by_label(
                    "Başlık"
                )
                headline.fill("Elle düzenlenmiş sentetik başlık")
                page.get_by_role("button", name="Metinleri kaydet").click()
                page.wait_for_url("**creative=saved")
                self.assertEqual(
                    page.locator(".creative-variant")
                    .first.get_by_label("Başlık")
                    .input_value(),
                    "Elle düzenlenmiş sentetik başlık",
                )

                page.locator("#edit-brief").click()
                page.locator("#daily-limit").fill("1000")
                page.get_by_role("button", name="Örnek kampanyayı gör").click()
                page.wait_for_url("**campaign=*#kampanya-denemesi")
                self.assertFalse(page.locator(".creative-stale-note").count())
                warning = page.locator("#creative-regenerate-warning")
                self.assertTrue(warning.is_visible())
                regenerate = page.get_by_role(
                    "button", name="Örnekten yeni öneriler oluştur"
                )
                self.assertEqual(
                    regenerate.get_attribute("aria-describedby"),
                    "creative-regenerate-warning",
                )
                regenerate.click()
                page.wait_for_url("**creative=regenerated")
                self.assertEqual(
                    page.locator(".creative-variant")
                    .first.get_by_label("Başlık")
                    .input_value(),
                    "Örnek Ankara ev bakım işletmesi",
                )
            finally:
                browser.close()

    def test_budget_and_duration_errors_are_associated_and_focused(self):
        invalid_cases = (
            (
                "#daily-limit",
                "99",
                "(field) => { field.removeAttribute('min'); field.step = 'any'; }",
            ),
            (
                "#daily-limit",
                "100001",
                "(field) => { field.removeAttribute('max'); field.step = 'any'; }",
            ),
            (
                "#campaign-days",
                "21",
                "(field) => { const option = new Option('21 gün', '21'); "
                "field.add(option); field.value = '21'; }",
            ),
        )
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 390, "height": 844})
                for selector, invalid_value, bypass_native_constraint in invalid_cases:
                    with self.subTest(field=selector, value=invalid_value):
                        page.goto(self.live_server_url)
                        field = page.locator(selector)
                        field.evaluate(bypass_native_constraint)
                        if selector == "#campaign-days":
                            field.select_option(invalid_value)
                        else:
                            field.fill(invalid_value)

                        with page.expect_response(
                            lambda response: response.request.method == "POST"
                        ) as invalid_response:
                            page.get_by_role(
                                "button", name="Örnek kampanyayı gör"
                            ).click()
                        self.assertEqual(invalid_response.value.status, 200)
                        page.wait_for_load_state("domcontentloaded")
                        field_id = field.get_attribute("id")
                        page.wait_for_function(
                            f"document.activeElement.id === '{field_id}'",
                            timeout=3000,
                        )

                        self.assertEqual(field.get_attribute("aria-invalid"), "true")
                        error_id = field.get_attribute("aria-describedby")
                        self.assertEqual(error_id, f"{field.get_attribute('id')}-error")
                        self.assertTrue(page.locator(f"#{error_id}").inner_text())
                        self.assertEqual(
                            page.evaluate("document.activeElement.id"),
                            field.get_attribute("id"),
                        )
            finally:
                browser.close()

    def test_campaign_journey_fits_a_mobile_viewport(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 390, "height": 844})
                page.goto(self.live_server_url)

                self.assert_no_horizontal_overflow(page)
                self.assertEqual(page.locator("#campaign-brief").count(), 0)
                self.assertEqual(page.locator("#brand-context").count(), 0)
                self.assertEqual(page.locator("#target-audience").count(), 0)
                self.assertIn(
                    "sabit sentetik örneği kullanır",
                    page.locator(".simulation-note").first.inner_text(),
                )
                self.assertIn(
                    "Ankara bölgesinde ev bakım hizmeti",
                    page.locator(".synthetic-sample").inner_text(),
                )

                page.locator("#campaign-objective").focus()
                self.assertEqual(
                    page.evaluate("document.activeElement.id"), "campaign-objective"
                )
                page.keyboard.press("Tab")
                self.assertEqual(
                    page.evaluate("document.activeElement.id"), "daily-limit"
                )
                page.keyboard.press("Tab")
                self.assertEqual(
                    page.evaluate("document.activeElement.id"), "campaign-days"
                )
                page.keyboard.press("Tab")
                self.assertEqual(
                    page.evaluate("document.activeElement.id"), "create-preview"
                )
                page.keyboard.press("Enter")
                page.wait_for_url("**campaign=*#kampanya-denemesi")
                self.assertEqual(page.locator("#step-count").inner_text(), "2 / 3")
                studio_top = page.locator("#kampanya-denemesi").evaluate(
                    "element => element.getBoundingClientRect().top"
                )
                self.assertLess(studio_top, 120)
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
                    "button", name="Örnekten yeni öneriler oluştur"
                ).click()
                page.wait_for_url("**creative=regenerated")
                self.assertEqual(
                    page.get_by_role("status")
                    .filter(
                        has_text="Sentetik örnekten yeni metin önerileri hazırlandı."
                    )
                    .count(),
                    1,
                )

                page.get_by_role("button", name="Örnek rapor").click()
                self.assertEqual(page.locator("#step-count").inner_text(), "3 / 3")
                report_top = page.locator("#report-panel").evaluate(
                    "panel => panel.getBoundingClientRect().top"
                )
                self.assertGreaterEqual(report_top, 0)
                self.assertLess(report_top, page.evaluate("window.innerHeight"))
                self.assert_no_horizontal_overflow(page)

                page.get_by_role("button", name="Bu taslağı sil").click()
                page.wait_for_url("**draft=deleted#kampanya-denemesi")
                self.assertEqual(
                    page.get_by_role("status")
                    .filter(has_text="Taslak silindi ve bu oturumdan kaldırıldı.")
                    .count(),
                    1,
                )
                self.assertEqual(page.locator("#saved-campaign").count(), 0)
            finally:
                browser.close()

    def assert_no_horizontal_overflow(self, page):
        dimensions = page.evaluate(
            "({viewport: window.innerWidth, document: document.documentElement.scrollWidth})"
        )
        self.assertEqual(dimensions["document"], dimensions["viewport"])
