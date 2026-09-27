"""Tests for session-scoped synthetic campaign drafts."""

from datetime import timedelta

from django.contrib.sessions.models import Session
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from growthtwin.site.models import CampaignDraft


class CampaignDraftFlowTests(TestCase):
    def setUp(self):
        self.url = reverse("site:home")
        self.valid_data = {
            "brief": "Sentetik yerel mağaza tanıtımı",
            "daily_limit": "750",
            "duration_days": "14",
        }

    def test_valid_post_persists_and_refresh_shows_session_draft(self):
        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 302)
        draft = CampaignDraft.objects.get()
        self.assertEqual(draft.brief, self.valid_data["brief"])
        self.assertEqual(draft.daily_limit, 750)
        self.assertEqual(draft.duration_days, 14)
        self.assertEqual(draft.total_limit, 10500)
        self.assertEqual(draft.session_id, self.client.session.session_key)

        preview = self.client.get(response.url)
        self.assertContains(preview, 'id="saved-campaign"')
        self.assertContains(preview, "Sentetik yerel mağaza tanıtımı")
        self.assertContains(preview, 'data-daily-limit="750"')
        self.assertContains(preview, 'data-duration-days="14"')

    def test_edit_updates_the_existing_draft(self):
        self.client.post(self.url, self.valid_data)
        draft = CampaignDraft.objects.get()
        edit_data = {
            **self.valid_data,
            "campaign_id": str(draft.pk),
            "brief": "Sentetik güncellenmiş tanıtım",
            "daily_limit": "1250",
            "duration_days": "30",
        }

        response = self.client.post(self.url, edit_data)

        self.assertEqual(response.status_code, 302)
        draft.refresh_from_db()
        self.assertEqual(draft.brief, "Sentetik güncellenmiş tanıtım")
        self.assertEqual(draft.daily_limit, 1250)
        self.assertEqual(draft.duration_days, 30)
        self.assertEqual(CampaignDraft.objects.count(), 1)
        self.assertIn(str(draft.pk), response.url)

    def test_invalid_edit_does_not_change_the_existing_draft(self):
        self.client.post(self.url, self.valid_data)
        draft = CampaignDraft.objects.get()
        edit_data = {
            **self.valid_data,
            "campaign_id": str(draft.pk),
            "brief": "Sentetik geçersiz düzenleme",
            "daily_limit": "100001",
        }

        response = self.client.post(self.url, edit_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("daily_limit", response.context["form"].errors)
        draft.refresh_from_db()
        self.assertEqual(draft.brief, self.valid_data["brief"])
        self.assertEqual(draft.daily_limit, 750)
        self.assertEqual(draft.duration_days, 14)
        self.assertEqual(CampaignDraft.objects.count(), 1)

    def test_invalid_brief_budget_and_duration_are_not_saved(self):
        invalid_submissions = (
            ({**self.valid_data, "brief": "   "}, "brief"),
            ({**self.valid_data, "daily_limit": "99"}, "daily_limit"),
            ({**self.valid_data, "daily_limit": "100001"}, "daily_limit"),
            ({**self.valid_data, "duration_days": "21"}, "duration_days"),
        )

        for data, field in invalid_submissions:
            with self.subTest(field=field, value=data[field]):
                response = self.client.post(self.url, data)

                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context["form"].errors)
                self.assertFalse(CampaignDraft.objects.exists())

    def test_draft_cannot_be_read_from_a_different_session(self):
        response = self.client.post(self.url, self.valid_data)
        draft = CampaignDraft.objects.get()
        other_client = self.client_class()

        other_response = other_client.get(response.url)

        self.assertRedirects(other_response, self.url)
        self.assertNotIn(draft.brief.encode(), other_response.content)
        self.assertEqual(CampaignDraft.objects.count(), 1)

    def test_draft_cannot_be_changed_from_a_different_session(self):
        self.client.post(self.url, self.valid_data)
        draft = CampaignDraft.objects.get()
        other_client = self.client_class()
        edit_data = {
            **self.valid_data,
            "campaign_id": str(draft.pk),
            "brief": "Başka oturumdan değişiklik",
        }

        response = other_client.post(self.url, edit_data)

        self.assertRedirects(response, self.url)
        draft.refresh_from_db()
        self.assertEqual(draft.brief, self.valid_data["brief"])
        self.assertEqual(CampaignDraft.objects.count(), 1)

    def test_expired_session_cleanup_deletes_its_drafts(self):
        self.client.post(self.url, self.valid_data)
        draft = CampaignDraft.objects.get()
        session = Session.objects.get(pk=draft.session_id)
        session.expire_date = timezone.now() - timedelta(seconds=1)
        session.save(update_fields=("expire_date",))

        call_command("clearsessions")

        self.assertFalse(CampaignDraft.objects.exists())
