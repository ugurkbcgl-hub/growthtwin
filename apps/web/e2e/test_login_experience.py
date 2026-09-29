"""Browser checks for the GrowthTwin sign-in entry point."""

from django.test import LiveServerTestCase
from django.urls import reverse
from playwright.sync_api import sync_playwright


class LoginExperienceBrowserTests(LiveServerTestCase):
    """Keep sign-in clear, localized and connected to the intended next page."""

    def test_public_entry_opens_localized_login_and_shows_safe_error(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 390, "height": 844})
                page.goto(f"{self.live_server_url}{reverse('site:home')}")
                page.get_by_role("link", name="Giriş yap").click()
                page.wait_for_url("**/accounts/login/**")

                self.assertEqual(
                    page.get_by_role("heading", level=1).inner_text(),
                    "Tekrar hoş geldin",
                )
                self.assertIn(reverse("campaigns:list"), page.url)
                self.assertEqual(
                    page.locator("#id_username").get_attribute("autocomplete"),
                    "username",
                )
                self.assertEqual(
                    page.locator("#id_password").get_attribute("autocomplete"),
                    "current-password",
                )
                self.assertIn(
                    "herkese açık hesap oluşturma kapalıdır",
                    page.locator("body").inner_text(),
                )
                self.assert_no_horizontal_overflow(page)

                page.locator("#id_username").fill("synthetic-invalid-user")
                page.locator("#id_password").fill("not-a-real-password")
                page.get_by_role("button", name="Giriş yap").click()
                error = page.get_by_role("alert")
                self.assertTrue(error.is_visible())
                self.assertEqual(
                    error.inner_text(),
                    "Kullanıcı adı veya parola eşleşmedi. Bilgilerini kontrol edip tekrar dene.",
                )
                self.assertEqual(page.locator("#id_password").input_value(), "")
                self.assert_no_horizontal_overflow(page)
            finally:
                browser.close()

    def assert_no_horizontal_overflow(self, page):
        dimensions = page.evaluate(
            "({viewport: window.innerWidth, document: document.documentElement.scrollWidth})"
        )
        self.assertEqual(dimensions["document"], dimensions["viewport"])
