"""Explicit fixture-only session rebinding, never execution or OAuth recovery."""

import time
from datetime import timedelta
from unittest.mock import patch
from uuid import uuid4

from django.test import Client, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from . import authorization_views as views
from . import synthetic_authorization as rehearsal
from . import test_authorization_journey as fixtures
from .connector_identity import block_identity, rotate_generation
from .models import SyntheticAuthorizationAttempt as Attempt


@override_settings(
    SYNTHETIC_CONNECTOR_UI_ENABLED=True, SYNTHETIC_CONNECTOR_AUTHORIZATION_ENABLED=True
)
class AuthorizationRecoveryTests(TransactionTestCase):
    setUp = fixtures.AuthorizationJourneyTests.setUp
    form = fixtures.AuthorizationJourneyTests.form
    begin = fixtures.AuthorizationJourneyTests.begin
    result_form = fixtures.AuthorizationJourneyTests.result_form

    def recovery_form(self, client):
        response = client.get(
            reverse("authorization_rehearsal:recovery", args=[self.workspace.pk])
        )
        row = response.context["rows"][0]
        url = reverse(
            "authorization_rehearsal:recover",
            args=[
                self.workspace.pk,
                row["snapshot"].connection_id,
                row["snapshot"].attempt_id,
            ],
        )
        return url, {"token": row["token"], "synthetic_only": "yes"}

    def new_session(self):
        client = Client()
        client.force_login(self.owner)
        return client

    def test_lost_session_requires_explicit_rebind_and_preserves_receipt(self):
        status_url = self.begin()
        client = self.new_session()
        self.assertEqual(client.get(status_url).status_code, 404)
        before = list(Attempt.objects.values())
        with (
            patch.object(rehearsal, "begin_example") as begin,
            patch.object(rehearsal, "perform_example") as perform,
        ):
            url, data = self.recovery_form(client)
            self.assertNotIn(views.MARKER, client.session)
            for _ in range(2):
                self.assertEqual(client.post(url, data).url, status_url)
            begin.assert_not_called()
            perform.assert_not_called()
        self.assertEqual(list(Attempt.objects.values()), before)
        response = client.get(status_url)
        self.assertIsNotNone(response.context["token"])
        self.assertEqual(response.context["snapshot"].state, "pending")

    def test_csrf_confirmation_method_and_default_off(self):
        self.begin()
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        url, data = self.recovery_form(client)
        self.assertEqual(client.post(url, data).status_code, 403)
        csrf = client.cookies["csrftoken"].value
        self.assertEqual(
            client.post(
                url, {"token": data["token"]}, HTTP_X_CSRFTOKEN=csrf
            ).status_code,
            409,
        )
        self.assertEqual(client.post(url, data, HTTP_X_CSRFTOKEN=csrf).status_code, 302)
        self.assertEqual(client.get(url).status_code, 405)
        with override_settings(SYNTHETIC_CONNECTOR_UI_ENABLED=False):
            response = client.post(url, data, HTTP_X_CSRFTOKEN=csrf)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response["Cache-Control"], "no-store, private")

    def test_other_owner_and_other_session_ticket_rejected(self):
        self.begin()
        client = self.new_session()
        url, data = self.recovery_form(client)
        another = self.new_session()
        self.assertEqual(another.post(url, data).status_code, 409)
        another.force_login(self.other)
        self.assertEqual(another.post(url, data).status_code, 404)
        self.assertNotIn(views.MARKER, another.session)

    def test_tampered_expired_wrong_action_or_extra_input_denied(self):
        start_form = self.form()
        self.begin()
        client = self.new_session()
        url, data = self.recovery_form(client)
        for invalid in (
            data | {"token": data["token"] + "x"},
            data | {"token": start_form["token"]},
            data | {"outcome": "accepted"},
            data | {"synthetic_only": ["yes", "yes"]},
        ):
            self.assertEqual(client.post(url, invalid).status_code, 409)
        with patch("django.core.signing.time.time", return_value=time.time() + 601):
            self.assertEqual(client.post(url, data).status_code, 409)
        self.assertNotIn(views.MARKER, client.session)

    def test_changed_receipt_deadline_rejects_rebind(self):
        self.begin()
        client = self.new_session()
        url, data = self.recovery_form(client)
        new = timezone.now() + timedelta(minutes=1)
        Attempt.objects.update(created_at=new, expires_at=new + timedelta(minutes=10))
        self.assertEqual(client.post(url, data).status_code, 409)
        self.assertNotIn(views.MARKER, client.session)

    def test_running_rebind_is_read_only_and_cannot_resume(self):
        status_url = self.begin()
        Attempt.objects.update(state="running")
        client = self.new_session()
        url, data = self.recovery_form(client)
        with patch.object(rehearsal, "_fixed_result") as fake:
            self.assertEqual(client.post(url, data).status_code, 302)
            response = client.get(status_url)
            self.assertContains(response, "otomatik tekrar yapılmaz")
            self.assertIsNone(response.context["token"])
            fake.assert_not_called()
        self.assertEqual(Attempt.objects.get().state, "running")

    def test_recovery_list_scoped_read_only_and_empty(self):
        url = reverse("authorization_rehearsal:recovery", args=[self.workspace.pk])
        self.assertContains(self.client.get(url), "Önceki örnek bulunmuyor")
        self.begin()
        before = list(Attempt.objects.values())
        self.assertContains(self.client.get(url), "Yalnızca örnek kayıt açılır")
        self.assertEqual(list(Attempt.objects.values()), before)

    def test_rotation_then_block_recovery_never_offers_perform(self):
        status_url = self.begin()
        client = self.new_session()
        url, data = self.recovery_form(client)
        newer = rotate_generation(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            request_id=uuid4(),
            expected_generation=self.identity.generation,
            expected_revision=self.identity.revision,
        )
        self.assertEqual(client.post(url, data).status_code, 302)
        self.assertIsNone(client.get(status_url).context["token"])
        block_identity(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            expected_generation=newer.generation,
            expected_revision=newer.revision,
        )
        self.assertEqual(client.post(url, data).status_code, 302)
        self.assertIsNone(client.get(status_url).context["token"])
        self.assertEqual(Attempt.objects.get().state, "pending")

    def test_expired_recovery_opens_history_without_extending_deadline(self):
        status_url = self.begin()
        old = timezone.now() - timedelta(days=1)
        Attempt.objects.update(created_at=old, expires_at=old + timedelta(minutes=10))
        client = self.new_session()
        url, data = self.recovery_form(client)
        self.assertEqual(client.post(url, data).status_code, 302)
        response = client.get(status_url)
        self.assertContains(response, "çalışma süresi doldu")
        self.assertIsNone(response.context["token"])
        self.assertEqual(Attempt.objects.get().expires_at, old + timedelta(minutes=10))

    def test_terminal_recovery_only_displays_saved_outcome(self):
        for example, state in ((0, "accepted"), (1, "rejected")):
            status_url = self.begin(example=example)
            self.client.post(status_url + "perform/", self.result_form(status_url))
            client = self.new_session()
            url, data = self.recovery_form(client)
            with patch.object(rehearsal, "_fixed_result") as fake:
                self.assertEqual(client.post(url, data).status_code, 302)
                self.assertIsNone(client.get(status_url).context["token"])
                fake.assert_not_called()
            self.assertEqual(client.get(status_url).context["snapshot"].state, state)
