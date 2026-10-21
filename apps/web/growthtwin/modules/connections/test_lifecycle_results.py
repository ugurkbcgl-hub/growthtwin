"""Bounded fake results: owner/CSRF/signed scope, replay and database races."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Barrier
from unittest.mock import patch
from uuid import uuid4

from django.core import signing
from django.db import close_old_connections
from django.test import (
    Client,
    TestCase,
    TransactionTestCase,
    override_settings,
    skipUnlessDBFeature,
)
from django.urls import reverse

from .lifecycle_decision import RemoteStop
from .lifecycle_journey import EXAMPLES, example_id, start_example
from .lifecycle_results import complete_example
from .lifecycle_store import ClosureConflict, get_synthetic_closure
from .lifecycle_views import RESULT_SALT
from .models import SyntheticClosureOperation, SyntheticClosureRequest
from .test_lifecycle_journey import JourneyFixture


@override_settings(SYNTHETIC_CLOSURE_UI_ENABLED=True)
class SyntheticClosureResultTests(JourneyFixture, TestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.owner)
        self.record = start_example(owner=self.owner, workspace_id=self.workspace.pk)
        self.url = reverse("closure:result", args=[self.workspace.pk, self.request_id])
        self.token = self.client.get(self.status).context["result_token"]

    def post(self, **changes):
        return self.client.post(
            self.url, {"synthetic_only": "yes", "token": self.token} | changes
        )

    def read(self):
        return get_synthetic_closure(
            owner=self.owner, workspace_id=self.workspace.pk, request_id=self.request_id
        )

    def test_confirmed_and_uncertain_are_separate_server_owned_examples(self):
        for example, _ in EXAMPLES:
            request_id = example_id(self.workspace.pk, "request", example)
            start = reverse("closure:start-example", args=[self.workspace.pk, example])
            status = reverse("closure:status", args=[self.workspace.pk, request_id])
            result = reverse("closure:result", args=[self.workspace.pk, request_id])
            self.assertRedirects(
                self.client.post(start, {"synthetic_only": "yes"}), status
            )
            token = self.client.get(status).context["result_token"]
            self.assertRedirects(
                self.client.post(result, {"synthetic_only": "yes", "token": token}),
                status,
            )
            record = get_synthetic_closure(
                owner=self.owner, workspace_id=self.workspace.pk, request_id=request_id
            )
            expected = (
                RemoteStop.CONFIRMED if example == "durdurma" else RemoteStop.UNCERTAIN
            )
            self.assertEqual(record.snapshot.remote_stop, expected)
            self.assertEqual(record.revision, 2)
            self.assertIsNone(record.pending)
            self.assertEqual(len(record.seen_events), 1)
            response = self.client.get(status)
            self.assertContains(response, "Yalnızca örnek durum")
            self.assertContains(response, "Google yetki iptali doğrulanamadı.")
            self.assertContains(response, "Yerel yetki bilgisi hâlâ mevcut.")
            self.assertContains(
                response,
                "Uzak kampanyanın durduğu doğrulandı."
                if example == "durdurma"
                else "Uzak kampanyanın durduğu doğrulanamadı.",
            )
            self.assertIsNone(response.context["result_token"])
            self.assertNotContains(response, "Örnek sonucu göster")
        self.assertEqual(SyntheticClosureRequest.objects.count(), 2)
        self.assertEqual(SyntheticClosureOperation.objects.count(), 2)

    def test_replay_does_not_call_adapter_again_or_create_another_operation(self):
        with patch(
            "growthtwin.modules.connections.lifecycle_fake.stop_result",
            return_value=RemoteStop.CONFIRMED,
        ) as fake:
            self.assertEqual(self.post().status_code, 302)
            first = self.read()
            self.assertEqual(self.post().status_code, 302)
            self.assertEqual(self.read(), first)
            fake.assert_called_once_with("durdurma")
        self.assertEqual(SyntheticClosureOperation.objects.count(), 1)
        self.assertEqual(len(first.seen_events), 1)
        self.client.get(self.status)
        self.client.post(self.start, {"synthetic_only": "yes"})
        self.assertEqual(self.read(), first)

    def test_get_head_and_other_methods_never_apply_a_result(self):
        for method in (
            self.client.get,
            self.client.head,
            self.client.put,
            self.client.patch,
            self.client.delete,
        ):
            self.assertEqual(method(self.url).status_code, 405)
        self.assertEqual(self.read(), self.record)

    def test_missing_confirmation_extra_evidence_and_duplicate_fields_rejected(self):
        for payload in (
            {"token": self.token},
            {"token": self.token, "synthetic_only": "no"},
            {"token": [self.token, self.token], "synthetic_only": "yes"},
            {"token": self.token, "synthetic_only": "yes", "remote_stop": "confirmed"},
            {"token": self.token, "synthetic_only": "yes", "revision": 1},
            {"token": self.token, "synthetic_only": "yes", "proof": "forbidden-copy"},
        ):
            response = self.client.post(self.url, payload)
            self.assertEqual(response.status_code, 400)
            self.assertNotContains(response, "forbidden-copy", status_code=400)
        self.assertEqual(self.read(), self.record)

    def test_csrf_required_and_valid_csrf_can_apply(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        response = client.get(self.status)
        token = response.context["result_token"]
        payload = {"token": token, "synthetic_only": "yes"}
        self.assertEqual(client.post(self.url, payload).status_code, 403)
        csrf = client.cookies["csrftoken"].value
        self.assertEqual(
            client.post(self.url, payload, HTTP_X_CSRFTOKEN=csrf).status_code, 302
        )

    def test_tampered_expired_and_wrong_scoped_tokens_fail_without_writes(self):
        payload = signing.loads(self.token, salt=RESULT_SALT)
        for changes in (
            {"owner": self.other.pk},
            {"workspace": self.foreign.pk},
            {"request": str(uuid4())},
            {"operation": str(uuid4())},
            {"revision": 0},
            {"revision": True},
            {"revision": 2},
            {"extra": "forbidden-copy"},
        ):
            token = signing.dumps(payload | changes, salt=RESULT_SALT)
            self.assertEqual(self.post(token=token).status_code, 409)
        self.assertEqual(self.post(token=self.token + "bad").status_code, 409)
        with patch("django.core.signing.time.time", return_value=0):
            expired = signing.dumps(payload, salt=RESULT_SALT)
        self.assertEqual(self.post(token=expired).status_code, 409)
        self.assertEqual(self.read(), self.record)

    def test_anonymous_foreign_and_inactive_cannot_apply_even_with_a_token(self):
        self.client.logout()
        self.assertEqual(self.post().status_code, 302)
        self.client.force_login(self.other)
        self.assertEqual(self.post().status_code, 404)
        self.owner.is_active = False
        self.owner.save(update_fields=["is_active"])
        self.client.force_login(self.owner)
        self.assertEqual(self.post().status_code, 302)
        self.assertEqual(SyntheticClosureRequest.objects.get().revision, 1)

    def test_unknown_example_is_not_created(self):
        start = reverse("closure:start-example", args=[self.workspace.pk, "unknown"])
        self.assertEqual(
            self.client.post(start, {"synthetic_only": "yes"}).status_code, 404
        )
        self.assertEqual(SyntheticClosureRequest.objects.count(), 1)

    def test_case_token_cannot_be_applied_to_the_other_case(self):
        other = start_example(
            owner=self.owner, workspace_id=self.workspace.pk, example="belirsiz"
        )
        url = reverse(
            "closure:result", args=[self.workspace.pk, other.identity.request_id]
        )
        self.assertEqual(
            self.client.post(
                url, {"synthetic_only": "yes", "token": self.token}
            ).status_code,
            409,
        )
        self.assertEqual(
            SyntheticClosureRequest.objects.get(pk=other.identity.request_id).revision,
            1,
        )

    def test_stale_or_corrupt_state_cannot_invoke_the_adapter_or_be_reset(self):
        original = SyntheticClosureRequest.objects.get().state
        state = deepcopy(original)
        state["snapshot"]["recovery_verified"] = False
        SyntheticClosureRequest.objects.update(state=state)
        with patch(
            "growthtwin.modules.connections.lifecycle_fake.stop_result",
            side_effect=AssertionError,
        ):
            self.assertEqual(self.post().status_code, 409)
        self.assertEqual(SyntheticClosureRequest.objects.get().state, state)

    def test_adapter_wrong_result_and_commit_failure_do_not_change_state(self):
        with patch(
            "growthtwin.modules.connections.lifecycle_fake.stop_result",
            return_value=RemoteStop.UNCERTAIN,
        ):
            self.assertEqual(self.post().status_code, 409)
        self.assertEqual(self.read(), self.record)
        with patch(
            "growthtwin.modules.connections.lifecycle_results.observe_synthetic_closure",
            side_effect=ClosureConflict,
        ):
            self.assertEqual(self.post().status_code, 409)
        self.assertEqual(self.read(), self.record)
        self.assertEqual(SyntheticClosureOperation.objects.count(), 1)

    def test_default_off_and_private_headers_cover_result_errors(self):
        with override_settings(SYNTHETIC_CLOSURE_UI_ENABLED=False):
            response = self.post()
            self.assertEqual(response.status_code, 404)
        for response in (response, self.client.get(self.url), self.post(token="bad")):
            self.assertEqual(response["Cache-Control"], "no-store, private")
            self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")

    def test_no_credentials_or_provider_calls_in_either_fixture_result(self):
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
            self.assertEqual(self.post().status_code, 302)

    def test_modified_event_identity_cannot_be_accepted_as_exact_replay(self):
        self.post()
        row = SyntheticClosureRequest.objects.get()
        row.state["seen_events"][0]["event_id"] = str(uuid4())
        row.save(update_fields=["state"])
        with patch(
            "growthtwin.modules.connections.lifecycle_fake.stop_result",
            side_effect=AssertionError,
        ):
            self.assertEqual(self.post().status_code, 409)
        self.assertEqual(SyntheticClosureRequest.objects.get().revision, 2)


class PostgreSQLResultRaceTests(JourneyFixture, TransactionTestCase):
    @skipUnlessDBFeature("has_select_for_update")
    def test_duplicate_result_writers_commit_one_event_and_invoke_fake_once(self):
        record = start_example(owner=self.owner, workspace_id=self.workspace.pk)
        barrier = Barrier(2)

        def writer(_):
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                return complete_example(
                    owner=self.owner,
                    workspace_id=self.workspace.pk,
                    request_id=self.request_id,
                    operation_id=record.pending.operation_id,
                    expected_revision=1,
                )
            finally:
                close_old_connections()

        with patch(
            "growthtwin.modules.connections.lifecycle_fake.stop_result",
            return_value=RemoteStop.CONFIRMED,
        ) as fake:
            with ThreadPoolExecutor(max_workers=2) as pool:
                first, second = pool.map(writer, range(2))
            fake.assert_called_once_with("durdurma")
        self.assertEqual(first, second)
        self.assertEqual(first.revision, 2)
        self.assertEqual(len(first.seen_events), 1)
        self.assertEqual(SyntheticClosureOperation.objects.count(), 1)
