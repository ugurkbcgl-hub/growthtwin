"""Focused owner/CSRF/replay tests with isolated synthetic databases only."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Barrier
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import close_old_connections
from django.test import (
    Client,
    TestCase,
    TransactionTestCase,
    override_settings,
    skipUnlessDBFeature,
)
from django.urls import reverse

from growthtwin.modules.workspaces.models import Workspace

from .lifecycle_decision import RemoteStop
from .lifecycle_journey import example_id, start_example
from .lifecycle_observation import Observation
from .lifecycle_store import (
    ClosureConflict,
    get_synthetic_closure,
    observe_synthetic_closure,
)
from .models import SyntheticClosureOperation, SyntheticClosureRequest


class JourneyFixture:
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="journey-owner")
        self.other = get_user_model().objects.create_user(username="journey-other")
        self.workspace = Workspace.objects.create(
            owner=self.owner, name="Örnek çalışma alanı"
        )
        self.foreign = Workspace.objects.create(
            owner=self.other, name="Başkasının alanı"
        )
        self.overview = reverse("closure:overview")
        self.start = reverse("closure:start", args=[self.workspace.pk])
        self.request_id = example_id(self.workspace.pk, "request")
        self.status = reverse(
            "closure:status", args=[self.workspace.pk, self.request_id]
        )


@override_settings(SYNTHETIC_CLOSURE_UI_ENABLED=True)
class SyntheticClosureJourneyTests(JourneyFixture, TestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.owner)

    def test_overview_is_owner_only_and_does_not_create_anything(self):
        response = self.client.get(self.overview)
        self.assertContains(response, self.workspace.name)
        self.assertNotContains(response, self.foreign.name)
        self.assertContains(response, "Sentetik provayı başlat")
        self.assertContains(response, 'name="synthetic_only"')
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, "Sentetik prova · Gerçek işlem yapılmaz")
        self.assertNotContains(response, "<script")
        self.assertEqual(SyntheticClosureRequest.objects.count(), 0)
        self.assertEqual(SyntheticClosureOperation.objects.count(), 0)

    def test_anonymous_requests_redirect_to_login_without_creating_records(self):
        self.client.logout()
        for response in (
            self.client.get(self.overview),
            self.client.get(self.status),
            self.client.post(self.start, {"synthetic_only": "yes"}),
        ):
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith(reverse("login")))
        self.assertEqual(SyntheticClosureRequest.objects.count(), 0)

    def test_disabled_routes_and_campaign_link_are_hidden(self):
        with override_settings(SYNTHETIC_CLOSURE_UI_ENABLED=False):
            for response in (
                self.client.get(self.overview),
                self.client.get(self.status),
                self.client.post(self.start, {"synthetic_only": "yes"}),
            ):
                self.assertEqual(response.status_code, 404)
                self.assertIn("no-store", response["Cache-Control"])
            self.assertNotContains(
                self.client.get(reverse("campaigns:list")), self.overview
            )
        self.assertEqual(SyntheticClosureRequest.objects.count(), 0)

    def test_enabled_campaign_list_links_to_journey(self):
        self.assertContains(self.client.get(reverse("campaigns:list")), self.overview)

    def test_get_and_head_on_start_never_start_work(self):
        for method in (self.client.get, self.client.head):
            self.assertEqual(method(self.start).status_code, 405)
        self.assertEqual(SyntheticClosureRequest.objects.count(), 0)

    def test_csrf_required_and_valid_csrf_can_start(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(
            client.post(self.start, {"synthetic_only": "yes"}).status_code, 403
        )
        self.assertEqual(SyntheticClosureRequest.objects.count(), 0)
        client.get(self.overview)
        token = client.cookies["csrftoken"].value
        self.assertEqual(
            client.post(
                self.start, {"synthetic_only": "yes"}, HTTP_X_CSRFTOKEN=token
            ).status_code,
            302,
        )
        self.assertEqual(SyntheticClosureOperation.objects.count(), 1)

    def test_missing_wrong_duplicate_and_extra_proof_fields_are_rejected(self):
        for payload in (
            {},
            {"synthetic_only": "no"},
            {"synthetic_only": ["yes", "yes"]},
            {"synthetic_only": "yes", "revocation": "confirmed"},
            {"synthetic_only": "yes", "request_id": str(uuid4())},
            {"synthetic_only": "yes", "workspace_id": self.foreign.pk},
            {"synthetic_only": "yes", "snapshot": "forbidden-copy"},
        ):
            response = self.client.post(self.start, payload)
            self.assertEqual(response.status_code, 400)
            self.assertNotContains(response, "forbidden-copy", status_code=400)
        self.assertEqual(SyntheticClosureRequest.objects.count(), 0)
        self.assertEqual(SyntheticClosureOperation.objects.count(), 0)

    def test_foreign_workspace_and_request_ids_are_404(self):
        foreign_start = reverse("closure:start", args=[self.foreign.pk])
        self.assertEqual(
            self.client.post(foreign_start, {"synthetic_only": "yes"}).status_code, 404
        )
        self.client.post(self.start, {"synthetic_only": "yes"})
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(self.status).status_code, 404)
        self.assertEqual(
            self.client.post(self.start, {"synthetic_only": "yes"}).status_code, 404
        )
        other_status = reverse(
            "closure:status", args=[self.foreign.pk, self.request_id]
        )
        self.assertEqual(self.client.get(other_status).status_code, 404)
        self.assertEqual(SyntheticClosureRequest.objects.count(), 1)

    def test_inactive_user_cannot_read_or_start(self):
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)
        self.assertEqual(self.client.get(self.overview).status_code, 302)
        self.assertEqual(
            self.client.post(self.start, {"synthetic_only": "yes"}).status_code, 302
        )
        self.assertFalse(SyntheticClosureRequest.objects.exists())

    def test_start_redirect_and_replay_keep_one_request_and_one_receipt(self):
        for _ in range(2):
            response = self.client.post(self.start, {"synthetic_only": "yes"})
            self.assertRedirects(response, self.status)
        self.assertEqual(SyntheticClosureRequest.objects.count(), 1)
        self.assertEqual(SyntheticClosureOperation.objects.count(), 1)
        row = SyntheticClosureRequest.objects.get()
        self.assertEqual(row.revision, 1)
        self.assertEqual(row.state["seen_events"], [])
        self.assertEqual(row.state["snapshot"]["remote_stop"], "pending")
        self.assertEqual(row.state["snapshot"]["revocation"], "unverified")
        overview = self.client.get(self.overview)
        self.assertContains(overview, "Kaydedilen provayı aç")
        self.assertNotContains(overview, "Sentetik provayı başlat")

    def test_status_refresh_head_and_query_data_do_not_modify_or_invent_results(self):
        self.client.post(self.start, {"synthetic_only": "yes"})
        before = deepcopy(SyntheticClosureRequest.objects.get().state)
        for _ in range(2):
            response = self.client.get(self.status)
            self.assertContains(response, "İstek kaydedildi, sonuç bekleniyor")
            self.assertContains(response, "Uzak kampanyayı durdurma bekliyor.")
            self.assertContains(response, "Google yetki iptali doğrulanamadı.")
            self.assertContains(response, "gerçek hesabının durumunu göstermez")
            self.assertNotContains(response, "<script")
            self.assertNotContains(response, 'action="' + self.start)
        head = self.client.head(self.status)
        self.assertEqual(head.status_code, 200)
        self.assertEqual(head.content, b"")
        response = self.client.get(
            self.status, {"revocation": "confirmed", "value": "forbidden-copy"}
        )
        self.assertNotContains(response, "forbidden-copy")
        self.assertContains(response, "Google yetki iptali doğrulanamadı.")
        self.assertEqual(SyntheticClosureRequest.objects.get().state, before)
        self.assertEqual(SyntheticClosureOperation.objects.count(), 1)

    def test_status_is_read_only_and_other_methods_cannot_mutate(self):
        self.client.post(self.start, {"synthetic_only": "yes"})
        before = deepcopy(SyntheticClosureRequest.objects.get().state)
        for url in (self.status, self.overview):
            for method in (
                self.client.post,
                self.client.put,
                self.client.patch,
                self.client.delete,
            ):
                self.assertEqual(method(url).status_code, 405)
        for method in (self.client.put, self.client.patch, self.client.delete):
            self.assertEqual(method(self.start).status_code, 405)
        self.assertEqual(SyntheticClosureRequest.objects.get().state, before)

    def test_creation_and_issuance_failure_roll_back_together(self):
        with patch(
            "growthtwin.modules.connections.lifecycle_journey.issue_synthetic_ticket",
            side_effect=ClosureConflict,
        ):
            self.assertEqual(
                self.client.post(self.start, {"synthetic_only": "yes"}).status_code, 409
            )
        self.assertFalse(SyntheticClosureRequest.objects.exists())
        self.assertFalse(SyntheticClosureOperation.objects.exists())

    def test_repeated_start_preserves_an_internally_observed_fixture_result(self):
        record = start_example(owner=self.owner, workspace_id=self.workspace.pk)
        observed = observe_synthetic_closure(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            event=Observation(
                record.identity,
                record.revision,
                uuid4(),
                record.pending,
                RemoteStop.CONFIRMED,
            ),
        ).record
        self.assertRedirects(
            self.client.post(self.start, {"synthetic_only": "yes"}), self.status
        )
        self.assertEqual(
            get_synthetic_closure(
                owner=self.owner,
                workspace_id=self.workspace.pk,
                request_id=self.request_id,
            ),
            observed,
        )
        response = self.client.get(self.status)
        self.assertContains(response, "Uzak kampanyanın durduğu doğrulandı.")
        self.assertContains(response, "Google yetki iptali doğrulanamadı.")
        self.assertContains(response, "Yalnızca örnek durum")
        self.assertNotContains(response, "İstek kaydedildi, sonuç bekleniyor")
        self.assertEqual(SyntheticClosureOperation.objects.count(), 1)

    def test_corrupt_state_is_generic_409_and_is_not_reset(self):
        self.client.post(self.start, {"synthetic_only": "yes"})
        row = SyntheticClosureRequest.objects.get()
        row.state["extra"] = "forbidden-copy"
        row.save(update_fields=["state"])
        for response in (
            self.client.get(self.status),
            self.client.post(self.start, {"synthetic_only": "yes"}),
        ):
            self.assertEqual(response.status_code, 409)
            self.assertNotContains(response, "forbidden-copy", status_code=409)
        self.assertEqual(SyntheticClosureRequest.objects.get().state, row.state)
        self.assertEqual(SyntheticClosureOperation.objects.count(), 1)

    def test_no_workspace_is_created_by_overview(self):
        self.client.force_login(get_user_model().objects.create_user(username="empty"))
        before = Workspace.objects.count()
        self.assertContains(self.client.get(self.overview), "Henüz çalışma alanın yok")
        self.assertEqual(Workspace.objects.count(), before)

    def test_private_headers_include_errors_and_csrf_rejections(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)
        for response in (
            self.client.get(self.overview),
            self.client.get(self.status),
            self.client.get(self.start),
            csrf_client.post(self.start),
        ):
            self.assertIn("no-store", response["Cache-Control"])
            self.assertIn("private", response["Cache-Control"])
            self.assertEqual(response["Referrer-Policy"], "same-origin")
            self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")

    def test_all_routes_do_not_read_credentials_or_call_providers(self):
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
            self.assertEqual(self.client.get(self.overview).status_code, 200)
            self.assertEqual(
                self.client.post(self.start, {"synthetic_only": "yes"}).status_code, 302
            )
            self.assertEqual(self.client.get(self.status).status_code, 200)


class PostgreSQLJourneyRaceTests(JourneyFixture, TransactionTestCase):
    @skipUnlessDBFeature("has_select_for_update")
    def test_two_start_requests_commit_one_example_and_one_operation(self):
        barrier = Barrier(2)

        def writer(_):
            close_old_connections()
            try:
                owner = get_user_model().objects.get(pk=self.owner.pk)
                barrier.wait(timeout=10)
                return start_example(owner=owner, workspace_id=self.workspace.pk)
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            first, second = pool.map(writer, range(2))
        self.assertEqual(first, second)
        self.assertEqual(first.revision, 1)
        self.assertEqual(SyntheticClosureRequest.objects.count(), 1)
        self.assertEqual(SyntheticClosureOperation.objects.count(), 1)
        self.assertEqual(
            get_synthetic_closure(
                owner=self.owner,
                workspace_id=self.workspace.pk,
                request_id=self.request_id,
            ),
            first,
        )
