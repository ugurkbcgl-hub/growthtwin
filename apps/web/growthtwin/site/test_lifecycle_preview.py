"""Focused checks for the fixed-synthetic, read-only lifecycle preview."""

from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse

from .lifecycle_preview import SCENARIOS


class LifecyclePreviewTests(SimpleTestCase):
    def setUp(self):
        self.url = reverse("site:lifecycle-preview")

    def test_each_scenario_is_anonymous_data_free_and_has_selected_navigation(self):
        with (
            patch(
                "growthtwin.modules.connections.backend._read",
                side_effect=AssertionError,
            ),
            patch(
                "growthtwin.modules.connections.backend._post",
                side_effect=AssertionError,
            ),
        ):
            for key, label in SCENARIOS:
                with self.subTest(key=key):
                    response = self.client.get(self.url, {"senaryo": key})
                    self.assertContains(response, label)
                    self.assertContains(
                        response, "Sentetik önizleme · Gerçek işlem yapılmaz"
                    )
                    self.assertContains(response, "Yalnızca örnek sonuç")
                    self.assertContains(response, 'aria-current="page"', count=1)
                    self.assertContains(
                        response, 'name="robots" content="noindex, nofollow"'
                    )
                    self.assertContains(response, 'lang="tr"')
                    self.assertNotContains(response, "<form")
                    self.assertNotContains(response, "<input")
                    self.assertNotContains(response, "<script")
                    self.assertFalse(response.cookies)
                    for target, _ in SCENARIOS:
                        self.assertContains(
                            response, f"?senaryo={target}#scenario-result"
                        )

    def test_default_waiting_and_home_footer_entry(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Mevcut isteğin sonucu beklenmeli")
        home = self.client.get(reverse("site:home"))
        self.assertContains(home, f'href="{self.url}"')

    def test_replay_is_explained_without_resend(self):
        response = self.client.get(self.url, {"senaryo": "tekrar"})
        self.assertContains(response, "İkinci işlem oluşturulmadı.")
        self.assertContains(response, "Uzak kampanyayı durdurma bekliyor.")

    def test_urgent_revocation_does_not_imply_stop_or_local_secret_removal(self):
        response = self.client.get(self.url, {"senaryo": "acil"})
        self.assertContains(response, "Google yetki iptali doğrulandı.")
        self.assertContains(response, "Uzak kampanyanın durduğu doğrulanamadı.")
        self.assertContains(response, "Yerel yetki bilgisi hâlâ mevcut.")
        self.assertNotContains(response, "Uzak kampanyanın durduğu doğrulandı.")

    def test_recovery_shows_no_trusted_success_from_old_state(self):
        response = self.client.get(self.url, {"senaryo": "kurtarma"})
        self.assertContains(response, "eski sonuçlar güncel kabul edilmedi.")
        self.assertNotContains(response, "Google yetki iptali doğrulandı.")

    def test_local_erasure_is_not_total_completion(self):
        response = self.client.get(self.url, {"senaryo": "temizlik"})
        self.assertContains(response, "Yerel veri temizliği kaydı tamamlandı")
        self.assertContains(response, "Yedek kopyaları: temizlik doğrulanamadı.")
        self.assertContains(
            response, "Alıcı ve yedek kopyalarının temizliği ayrı ayrı doğrulanmalı."
        )

    def test_write_methods_rejected_and_head_supported(self):
        for method in ("post", "put", "patch", "delete"):
            self.assertEqual(getattr(self.client, method)(self.url).status_code, 405)
        response = self.client.head(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")

    def test_unknown_scenario_is_not_reflected(self):
        response = self.client.get(self.url, {"senaryo": "synthetic-untrusted-marker"})
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, "synthetic-untrusted-marker", status_code=404)

    def test_extra_inputs_cannot_change_fixed_evidence(self):
        first = self.client.get(self.url, {"senaryo": "acil"})
        second = self.client.get(
            self.url,
            {
                "senaryo": "acil",
                "workspace_id": "synthetic-untrusted-marker",
                "revocation": "false",
                "message": "synthetic-untrusted-marker",
            },
        )
        self.assertEqual(first.content, second.content)
