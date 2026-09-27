"""Browser-level verification of the synthetic profile-edit path."""

import secrets

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from playwright.sync_api import sync_playwright

from e2e.profile_edit_flow import run_profile_edit_flow


class ProfileEditBrowserTests(LiveServerTestCase):
    """Exercise login, CSRF-protected editing, persistence, and logout."""

    def test_profile_edit_flow_in_a_real_browser(self):
        username = f"e2e-{secrets.token_hex(6)}"
        password = secrets.token_urlsafe(24)
        get_user_model().objects.create_user(username=username, password=password)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                context = browser.new_context()
                try:
                    page = context.new_page()
                    run_profile_edit_flow(
                        page,
                        self.live_server_url,
                        username,
                        password,
                    )
                finally:
                    context.close()
            finally:
                browser.close()
