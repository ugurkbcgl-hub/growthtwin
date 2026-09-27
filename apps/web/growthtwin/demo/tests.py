"""Focused tests for the synthetic profile edit flow."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from growthtwin.demo.models import DemoProfile


class DemoProfileEditTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            username="demo-owner",
            password="test-password-only",
        )
        other_user = user_model.objects.create_user(
            username="demo-other",
            password="test-password-only",
        )
        self.other_profile = DemoProfile.objects.create(
            owner=other_user,
            clinic_name="Sentetik Diğer Klinik",
            city="Bursa",
        )
        self.profile_url = reverse("demo:profile-edit")

    def test_profile_page_requires_login(self):
        response = self.client.get(self.profile_url)

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={self.profile_url}",
        )

    def test_user_can_edit_only_their_own_profile(self):
        DemoProfile.objects.create(
            owner=self.owner,
            clinic_name="Başlangıç Demo Kliniği",
            city="Ankara",
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            self.profile_url,
            {
                "clinic_name": "Sentetik Örnek Kliniği",
                "city": "İzmir",
                "phone": "0000000000",
                "website": "https://example.invalid",
            },
        )

        self.assertRedirects(response, self.profile_url)
        owner_profile = DemoProfile.objects.get(owner=self.owner)
        self.assertEqual(owner_profile.clinic_name, "Sentetik Örnek Kliniği")
        self.assertEqual(owner_profile.city, "İzmir")
        self.assertEqual(owner_profile.phone, "0000000000")
        self.assertEqual(owner_profile.website, "https://example.invalid")

        self.other_profile.refresh_from_db()
        self.assertEqual(self.other_profile.clinic_name, "Sentetik Diğer Klinik")
        self.assertEqual(self.other_profile.city, "Bursa")

    def test_user_sees_only_their_profile_and_get_creates_it(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Demo klinik profili")
        self.assertNotContains(response, "Sentetik Diğer Klinik")
        self.assertTrue(DemoProfile.objects.filter(owner=self.owner).exists())

    def test_invalid_website_is_not_saved(self):
        profile = DemoProfile.objects.create(
            owner=self.owner,
            clinic_name="Değişmeden Kalacak Demo",
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            self.profile_url,
            {
                "clinic_name": "Yeni Demo",
                "city": "Ankara",
                "phone": "",
                "website": "not-a-url",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("website", response.context["form"].errors)
        profile.refresh_from_db()
        self.assertEqual(profile.clinic_name, "Değişmeden Kalacak Demo")
