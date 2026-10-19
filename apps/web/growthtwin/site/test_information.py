"""Focused checks for static, anonymous, data-free preparation pages."""

from django.test import SimpleTestCase
from django.urls import reverse


class InformationPageTests(SimpleTestCase):
    pages = ("contact", "privacy", "terms")

    def test_anonymous_pages_render_without_database_or_session_writes(self):
        for page in self.pages:
            with self.subTest(page=page):
                response = self.client.get(reverse(f"site:{page}"))
                self.assertContains(response, "Taslak · Üretime hazır değil")
                self.assertContains(response, "19 Ekim 2026 · Hazırlık sürümü")
                self.assertContains(
                    response, 'name="robots" content="noindex, nofollow"'
                )
                self.assertContains(response, 'lang="tr"')
                self.assertNotContains(response, "<form")
                self.assertNotContains(response, "<input")
                self.assertNotContains(response, "<script")
                self.assertFalse(response.cookies)

    def test_pages_link_to_each_other_and_home(self):
        for page in self.pages:
            with self.subTest(page=page):
                response = self.client.get(reverse(f"site:{page}"))
                for target in (*self.pages, "home"):
                    self.assertContains(response, f'href="{reverse(f"site:{target}")}"')

    def test_home_footer_links_to_preparation_pages(self):
        response = self.client.get(reverse("site:home"))
        for page in self.pages:
            self.assertContains(response, f'href="{reverse(f"site:{page}")}"')

    def test_write_methods_are_rejected_and_head_is_supported(self):
        for page in self.pages:
            url = reverse(f"site:{page}")
            with self.subTest(page=page):
                for method in ("post", "put", "patch", "delete"):
                    self.assertEqual(getattr(self.client, method)(url).status_code, 405)
                response = self.client.head(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content, b"")

    def test_query_string_cannot_select_content_or_reflect_submitted_text(self):
        for page in self.pages:
            with self.subTest(page=page):
                response = self.client.get(
                    reverse(f"site:{page}"),
                    {"page_key": "unknown", "message": "synthetic-untrusted-marker"},
                )
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, "synthetic-untrusted-marker")
