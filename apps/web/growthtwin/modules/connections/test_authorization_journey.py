"""Synthetic endpoint security tests; no provider or credential access allowed."""

import time
from datetime import timedelta
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core import signing
from django.test import Client, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from growthtwin.modules.workspaces.models import Workspace

from . import authorization_views as views
from . import backend, candidate_readback, scoped_oauth_candidate
from . import synthetic_authorization as rehearsal
from .connector_identity import (
    block_identity,
    register_google_test_identity,
    rotate_generation,
)
from .models import ConnectorIdentity, ScopedOAuthCandidateAttempt
from .models import SyntheticAuthorizationAttempt as Attempt


@override_settings(
    SYNTHETIC_CONNECTOR_UI_ENABLED=True, SYNTHETIC_CONNECTOR_AUTHORIZATION_ENABLED=True
)
class AuthorizationJourneyTests(TransactionTestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="rehearsal-owner")
        self.other = get_user_model().objects.create_user(username="rehearsal-other")
        self.workspace = Workspace.objects.create(
            owner=self.owner, name="Sentetik alan"
        )
        self.identity = register_google_test_identity(
            owner=self.owner, workspace_id=self.workspace.pk, request_id=uuid4()
        )
        self.url = reverse("authorization_rehearsal:overview", args=[self.workspace.pk])
        self.start_url = reverse(
            "authorization_rehearsal:start", args=[self.workspace.pk]
        )
        self.client.force_login(self.owner)
        for module, names in (
            (backend, ("_client", "_read", "_write", "_post", "_token_path")),
            (scoped_oauth_candidate, ("begin_candidate", "consume_candidate")),
            (candidate_readback, ("inspect_candidate",)),
        ):
            for name in names:
                mock = patch.object(
                    module, name, side_effect=AssertionError("Forbidden real boundary")
                )
                mocked = mock.start()
                self.addCleanup(mock.stop)
                self.addCleanup(mocked.assert_not_called)

    def form(self, client=None, example=0):
        response = (client or self.client).get(self.url)
        return {
            "token": response.context["examples"][example]["token"],
            "synthetic_only": "yes",
        }

    def begin(self, client=None, example=0):
        response = (client or self.client).post(
            self.start_url, self.form(client, example)
        )
        self.assertEqual(response.status_code, 302)
        return response.url

    def result_form(self, status_url, client=None):
        response = (client or self.client).get(status_url)
        return {"token": response.context["token"], "synthetic_only": "yes"}

    def test_overview_is_read_only_explicit_and_no_script(self):
        before = list(ConnectorIdentity.objects.values())
        response = self.client.get(self.url)
        self.assertContains(response, "Sentetik prova · Gerçek hesap bağlanmaz")
        self.assertContains(response, 'name="synthetic_only"', count=2)
        self.assertNotContains(response, "<script")
        self.assertEqual(Attempt.objects.count(), 0)
        self.assertEqual(list(ConnectorIdentity.objects.values()), before)
        self.assertEqual(ScopedOAuthCandidateAttempt.objects.count(), 0)
        self.assertIn("no-store", response["Cache-Control"])

    def test_default_off_either_switch_hides_all_routes(self):
        status_url = self.begin()
        for setting in (
            "SYNTHETIC_CONNECTOR_UI_ENABLED",
            "SYNTHETIC_CONNECTOR_AUTHORIZATION_ENABLED",
        ):
            with override_settings(**{setting: False}):
                for response in (
                    self.client.get(self.url),
                    self.client.post(self.start_url),
                    self.client.get(status_url),
                    self.client.post(status_url + "perform/"),
                ):
                    self.assertEqual(response.status_code, 404)
        self.assertEqual(Attempt.objects.get().state, "pending")

    def test_anonymous_and_foreign_owner_cannot_use_pages(self):
        status_url = self.begin()
        self.client.logout()
        for url in (self.url, status_url):
            self.assertEqual(self.client.get(url).status_code, 302)
        self.assertEqual(self.client.post(self.start_url).status_code, 302)
        self.client.force_login(self.other)
        for url in (self.url, status_url):
            self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(self.start_url).status_code, 404)

    def test_missing_identity_never_creates_one(self):
        workspace = Workspace.objects.create(owner=self.owner, name="Empty")
        response = self.client.get(
            reverse("authorization_rehearsal:overview", args=[workspace.pk])
        )
        self.assertContains(response, "Prova henüz hazır değil")
        self.assertEqual(ConnectorIdentity.objects.count(), 1)
        self.assertEqual(Attempt.objects.count(), 0)

    def test_csrf_both_posts_and_method_restrictions(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        data = self.form(client)
        self.assertEqual(client.post(self.start_url, data).status_code, 403)
        token = client.cookies["csrftoken"].value
        response = client.post(self.start_url, data, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 302)
        status_url = response.url
        data = self.result_form(status_url, client)
        self.assertEqual(client.post(status_url + "perform/", data).status_code, 403)
        self.assertEqual(Attempt.objects.get().state, "pending")
        self.assertEqual(
            client.post(
                status_url + "perform/", data, HTTP_X_CSRFTOKEN=token
            ).status_code,
            302,
        )
        for url in (self.start_url, status_url + "perform/"):
            self.assertEqual(client.get(url).status_code, 405)
            self.assertEqual(client.head(url).status_code, 405)
        self.assertEqual(
            client.post(status_url, HTTP_X_CSRFTOKEN=token).status_code, 405
        )

    def test_begin_only_reserves_and_repeat_does_not_duplicate(self):
        data = self.form()
        with patch.object(
            rehearsal, "_fixed_result", wraps=rehearsal._fixed_result
        ) as fake:
            first = self.client.post(self.start_url, data)
            self.assertEqual(self.client.post(self.start_url, data).url, first.url)
            self.client.get(first.url)
            self.client.head(first.url)
            fake.assert_not_called()
        self.assertEqual(Attempt.objects.count(), 1)
        self.assertEqual(Attempt.objects.get().state, "pending")

    def test_two_fixed_outcomes_and_perform_replay(self):
        for example, state in ((0, "accepted"), (1, "rejected")):
            status_url = self.begin(example=example)
            data = self.result_form(status_url)
            with patch.object(
                rehearsal, "_fixed_result", wraps=rehearsal._fixed_result
            ) as fake:
                for _ in range(2):
                    self.assertEqual(
                        self.client.post(status_url + "perform/", data).status_code, 302
                    )
                fake.assert_called_once()
            response = self.client.get(status_url)
            self.assertEqual(response.context["snapshot"].state, state)
            self.assertIsNone(response.context["token"])
            self.assertContains(response, "Gerçek hesap bağlanmadı")
        self.assertEqual(Attempt.objects.count(), 2)
        self.assertEqual(ConnectorIdentity.objects.get().state, "quarantined")

    def test_missing_confirmation_extra_or_duplicate_inputs_rejected(self):
        data = self.form()
        for invalid in (
            data | {"synthetic_only": "no"},
            {"token": data["token"]},
            data | {"account_id": "fabricated"},
            data | {"token": [data["token"], data["token"]]},
            data | {"synthetic_only": ["yes", "yes"]},
        ):
            self.assertEqual(self.client.post(self.start_url, invalid).status_code, 409)
        self.assertEqual(Attempt.objects.count(), 0)

    def test_signed_token_tampering_wrong_action_and_expiry_rejected(self):
        data = self.form()
        self.assertEqual(
            self.client.post(
                self.start_url, data | {"token": data["token"] + "x"}
            ).status_code,
            409,
        )
        value = signing.loads(data["token"], salt=views.SALT)
        invalid = signing.dumps(value | {"action": "perform"}, salt=views.SALT)
        self.assertEqual(
            self.client.post(self.start_url, data | {"token": invalid}).status_code, 409
        )
        with patch("django.core.signing.time.time", return_value=time.time() + 601):
            self.assertEqual(self.client.post(self.start_url, data).status_code, 409)
        self.assertEqual(Attempt.objects.count(), 0)

    def test_other_session_and_rotated_session_cannot_reuse_form(self):
        data = self.form()
        other_session = Client()
        other_session.force_login(self.owner)
        self.assertEqual(other_session.post(self.start_url, data).status_code, 409)
        session = self.client.session
        session.cycle_key()
        self.client.cookies["sessionid"] = session.session_key
        self.assertEqual(self.client.post(self.start_url, data).status_code, 409)
        self.assertEqual(Attempt.objects.count(), 0)

    def test_result_is_bound_to_origin_session_and_route_attempt(self):
        status_url = self.begin()
        data = self.result_form(status_url)
        other_session = Client()
        other_session.force_login(self.owner)
        self.assertEqual(other_session.get(status_url).status_code, 404)
        self.assertEqual(
            other_session.post(status_url + "perform/", data).status_code, 409
        )
        wrong = status_url.replace(str(Attempt.objects.get().pk), str(uuid4()))
        self.assertEqual(self.client.post(wrong + "perform/", data).status_code, 404)
        self.assertEqual(Attempt.objects.get().state, "pending")

    def test_generation_change_before_begin_rejects_form(self):
        data = self.form()
        rotate_generation(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            request_id=uuid4(),
            expected_generation=self.identity.generation,
            expected_revision=self.identity.revision,
        )
        self.assertEqual(self.client.post(self.start_url, data).status_code, 409)
        self.assertEqual(Attempt.objects.count(), 0)

    def test_block_after_result_form_prevents_fake(self):
        status_url = self.begin()
        data = self.result_form(status_url)
        block_identity(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            expected_generation=self.identity.generation,
            expected_revision=self.identity.revision,
        )
        with patch.object(rehearsal, "_fixed_result") as fake:
            self.assertEqual(
                self.client.post(status_url + "perform/", data).status_code, 302
            )
            fake.assert_not_called()
        self.assertEqual(Attempt.objects.get().reason, "scope_changed")
        self.assertIsNone(self.client.get(status_url).context["token"])

    def test_running_result_never_reexecutes(self):
        status_url = self.begin()
        data = self.result_form(status_url)
        Attempt.objects.update(state="running")
        with patch.object(rehearsal, "_fixed_result") as fake:
            self.assertEqual(
                self.client.post(status_url + "perform/", data).status_code, 302
            )
            fake.assert_not_called()
        self.assertContains(self.client.get(status_url), "otomatik tekrar yapılmaz")
        self.assertIsNone(Attempt.objects.get().completed_at)

    def test_framework_errors_are_private_uncached_and_not_indexed(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        responses = [client.post(self.start_url)]
        with override_settings(SYNTHETIC_CONNECTOR_UI_ENABLED=False):
            responses.append(client.get(self.url))
        client.force_login(self.other)
        responses.append(client.get(self.url))
        self.assertEqual(
            [response.status_code for response in responses], [403, 404, 404]
        )
        for response in responses:
            self.assertEqual(response["Cache-Control"], "no-store, private")
            self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
            self.assertEqual(response["Referrer-Policy"], "same-origin")

    def test_expired_pending_page_is_read_only_and_old_result_cannot_run(self):
        status_url = self.begin()
        data = self.result_form(status_url)
        old = timezone.now() - timedelta(minutes=11)
        Attempt.objects.update(created_at=old, expires_at=old + timedelta(minutes=10))
        response = self.client.get(status_url)
        self.assertContains(response, "çalışma süresi doldu")
        self.assertIsNone(response.context["token"])
        self.assertEqual(Attempt.objects.get().state, "pending")
        with patch.object(rehearsal, "_fixed_result") as fake:
            self.assertEqual(
                self.client.post(status_url + "perform/", data).status_code, 302
            )
            fake.assert_not_called()
        self.assertEqual(Attempt.objects.get().state, "expired")

    def test_result_requires_confirmation_and_exact_input_shape(self):
        status_url = self.begin()
        data = self.result_form(status_url)
        for invalid in (
            {"token": data["token"]},
            data | {"result": "accepted"},
            data | {"synthetic_only": ["yes", "yes"]},
        ):
            self.assertEqual(
                self.client.post(status_url + "perform/", invalid).status_code, 409
            )
        self.assertEqual(Attempt.objects.get().state, "pending")
