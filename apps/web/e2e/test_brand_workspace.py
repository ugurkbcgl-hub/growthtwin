"""A complete synthetic multi-brand journey in the browser."""

import os
import re
import secrets
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.workspaces.models import (
    SYNTHETIC_BRAND_PRESETS,
    Brand,
    Workspace,
)


class BrandWorkspaceBrowserTests(LiveServerTestCase):
    def test_owner_creates_two_brands_and_keeps_identities_separate(self):
        password = secrets.token_urlsafe(32)
        owner = get_user_model().objects.create_user(
            username="synthetic-brand-browser-owner", password=password
        )
        workspace = Workspace.objects.create(owner=owner, name="Sentetik markalar")
        brand_ids = {}
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 390, "height": 844})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(self.live_server_url + reverse("brands:list"))
                page.locator("input[name='username']").fill(owner.username)
                page.locator("input[name='password']").fill(password)
                page.get_by_role("button", name="Giriş yap").click()
                page.wait_for_url("**" + reverse("brands:list"))
                for fixture in ("product", "service"):
                    page.goto(self.live_server_url + reverse("brands:create"))
                    page.locator("#id_workspace").select_option(str(workspace.pk))
                    page.locator("#id_fixture").select_option(fixture)
                    page.locator("main form button[type='submit']").click()
                    page.wait_for_url(re.compile(r"/workspace/brands/\d+/$"))
                    brand_ids[fixture] = int(page.url.rstrip("/").rsplit("/", 1)[-1])
                    self.assertFalse(
                        page.evaluate(
                            "document.documentElement.scrollWidth > innerWidth"
                        )
                    )
                page.goto(
                    self.live_server_url
                    + reverse("brands:edit", args=[brand_ids["product"]])
                )
                page.locator("#id_primary_color").select_option("#9A3F2D")
                page.locator("#id_tone").select_option("energetic")
                page.locator("main form button[type='submit']").click()
                page.wait_for_url(
                    "**" + reverse("brands:detail", args=[brand_ids["product"]])
                )
                screenshot_root = os.environ.get("YAPARO_BRAND_SCREENSHOT_DIR")
                if screenshot_root:
                    directory = Path(screenshot_root)
                    directory.mkdir(parents=True, exist_ok=True)
                    page.screenshot(
                        path=str(directory / "brand-mobile.png"), full_page=True
                    )
                    page.set_viewport_size({"width": 1440, "height": 1000})
                    page.screenshot(
                        path=str(directory / "brand-desktop.png"), full_page=True
                    )
                page.goto(self.live_server_url + reverse("brands:list"))
                expect(
                    page.get_by_role(
                        "heading", name=SYNTHETIC_BRAND_PRESETS["product"]["name"]
                    )
                ).to_be_visible()
                expect(
                    page.get_by_role(
                        "heading", name=SYNTHETIC_BRAND_PRESETS["service"]["name"]
                    )
                ).to_be_visible()
                self.assertEqual([], errors)
            finally:
                browser.close()

        product = Brand.objects.get(pk=brand_ids["product"], workspace=workspace)
        service = Brand.objects.get(pk=brand_ids["service"], workspace=workspace)
        self.assertEqual(2, product.current_version)
        self.assertEqual("energetic", product.current_identity.tone)
        self.assertNotEqual("energetic", product.identities.get(version=1).tone)
        self.assertEqual(1, service.current_version)
