"""Isolated desktop/mobile session rehearsal, with no Google boundary calls."""

import os
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from growthtwin.modules.connections import backend
from growthtwin.modules.connections.connector_identity import (
    register_google_test_identity,
)
from growthtwin.modules.connections.models import (
    ConnectorIdentity,
    SyntheticAuthorizationAttempt,
)
from growthtwin.modules.workspaces.models import Workspace


@override_settings(
    SYNTHETIC_CONNECTOR_UI_ENABLED=True,
    SYNTHETIC_CONNECTOR_AUTHORIZATION_ENABLED=True,
    GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=False,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class ConnectorRehearsalBrowserTests(StaticLiveServerTestCase):
    def test_desktop_mobile_keyboard_replay_and_no_real_boundary(self):
        owner = get_user_model().objects.create_user(username="browser-rehearsal")
        workspace = Workspace.objects.create(owner=owner, name="Örnek marka")
        register_google_test_identity(
            owner=owner, workspace_id=workspace.pk, request_id=uuid4()
        )
        self.client.force_login(owner)
        for name in ("_client", "_read", "_write", "_post", "_token_path"):
            mocked = patch.object(
                backend, name, side_effect=AssertionError("Forbidden real boundary")
            )
            boundary = mocked.start()
            self.addCleanup(mocked.stop)
            self.addCleanup(boundary.assert_not_called)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                context = browser.new_context(viewport={"width": 1440, "height": 1000})
                context.add_cookies(
                    [
                        {
                            "name": settings.SESSION_COOKIE_NAME,
                            "value": self.client.cookies[
                                settings.SESSION_COOKIE_NAME
                            ].value,
                            "url": self.live_server_url,
                        }
                    ]
                )
                page = context.new_page()
                page.goto(
                    self.live_server_url
                    + reverse("authorization_rehearsal:overview", args=[workspace.pk])
                )
                expect(
                    page.get_by_text(
                        "Sentetik prova · Gerçek hesap bağlanmaz", exact=True
                    )
                ).to_be_visible()
                page.wait_for_function(
                    "getComputedStyle(document.body).fontFamily.includes('Inter') || getComputedStyle(document.body).backgroundColor !== 'rgba(0, 0, 0, 0)'"
                )
                self._screenshot(page, "authorization-overview-desktop.png")
                checkbox = page.get_by_role("checkbox").first
                checkbox.focus()
                page.keyboard.press("Space")
                page.keyboard.press("Tab")
                expect(
                    page.get_by_role("button", name="Başarı örneği", exact=True)
                ).to_be_focused()
                page.keyboard.press("Enter")
                expect(
                    page.get_by_text(
                        "Örnek başlatıldı; sonuç henüz çalıştırılmadı.", exact=True
                    )
                ).to_be_visible()
                page.reload()
                expect(
                    page.get_by_text(
                        "Örnek başlatıldı; sonuç henüz çalıştırılmadı.", exact=True
                    )
                ).to_be_visible()
                page.set_viewport_size({"width": 390, "height": 844})
                self.assertLessEqual(
                    page.evaluate("document.documentElement.scrollWidth"), 390
                )
                self._screenshot(page, "authorization-pending-mobile.png")
                page.get_by_role("checkbox").check()
                page.get_by_role(
                    "button", name="Örnek sonucu çalıştır", exact=True
                ).click()
                expect(
                    page.get_by_text(
                        "Başarı örneği kaydedildi. Gerçek hesap bağlanmadı.", exact=True
                    )
                ).to_be_visible()
                expect(
                    page.get_by_role("button", name="Örnek sonucu çalıştır")
                ).to_have_count(0)
                self._screenshot(page, "authorization-accepted-mobile.png")
                page.reload()
                expect(
                    page.get_by_text(
                        "Başarı örneği kaydedildi. Gerçek hesap bağlanmadı.", exact=True
                    )
                ).to_be_visible()
                page.get_by_role("link", name="Prova seçeneklerine dön").click()
                page.get_by_role("checkbox").nth(1).check()
                page.get_by_role("button", name="Ret örneği", exact=True).click()
                page.get_by_role("checkbox").check()
                page.get_by_role("button", name="Örnek sonucu çalıştır").click()
                expect(
                    page.get_by_text(
                        "Örnek kabul edilmedi. Gerçek hesap bağlanmadı.", exact=True
                    )
                ).to_be_visible()
                self._screenshot(page, "authorization-rejected-mobile.png")
            finally:
                browser.close()
        self.assertEqual(ConnectorIdentity.objects.get().state, "quarantined")
        self.assertEqual(
            list(
                SyntheticAuthorizationAttempt.objects.order_by(
                    "created_at"
                ).values_list("state", flat=True)
            ),
            ["accepted", "rejected"],
        )

    def _screenshot(self, page, filename):
        destination = os.environ.get("GWT_REHEARSAL_SCREENSHOT_DIR")
        if destination:
            page.screenshot(path=str(Path(destination) / filename), full_page=True)
