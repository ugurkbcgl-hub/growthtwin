"""Scoped endpoint wiring exercised through mocked client/transport/storage only."""

import logging
import time
from unittest.mock import patch
from urllib.parse import parse_qs, urlencode, urlsplit

from django.test import Client, TransactionTestCase, override_settings
from django.urls import reverse

from . import scoped_views as views
from . import test_scoped_oauth_candidate as fixtures
from .google_oauth import (
    LOCAL_REDIRECT_URI,
    SCOPED_CALLBACK_PATH,
    SCOPED_REDIRECT_URI,
    AuthorizationRejected,
    LocalAuthorizationStore,
)
from .logging import OAuthCallbackFilter
from .models import ConnectorIdentity
from .models import ScopedOAuthCandidateAttempt as Attempt


@override_settings(
    DEBUG=False,
    ALLOWED_HOSTS=["127.0.0.1", "localhost"],
    GOOGLE_ADS_LOCAL_OAUTH_ENABLED=True,
    GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=True,
    GOOGLE_ADS_SCOPED_ENDPOINTS_ENABLED=True,
)
class ScopedEndpointTests(fixtures.CandidateFixture, TransactionTestCase):
    def setUp(self):
        super().setUp()
        context = self.settings(
            GOOGLE_ADS_LOCAL_OWNER_ID=str(self.owner.pk),
            GOOGLE_ADS_LOCAL_WORKSPACE_ID=str(self.workspace.pk),
        )
        context.enable()
        self.addCleanup(context.disable)
        self.client = Client(HTTP_HOST="127.0.0.1:8002")
        self.client.force_login(self.owner)
        self.overview = reverse("scoped_candidate:overview")
        self.start_url = reverse("scoped_candidate:start")
        self.retire_url = reverse("scoped_candidate:retire")

    def form(self, key="start_token", client=None):
        response = (client or self.client).get(self.overview)
        return {"token": response.context[key], "confirm": "yes"}

    def start(self, client=None):
        response = (client or self.client).post(
            self.start_url, self.form(client=client)
        )
        self.assertEqual(response.status_code, 302)
        params = parse_qs(urlsplit(response.url).query)
        self.assertEqual(params["redirect_uri"], [SCOPED_REDIRECT_URI])
        return params["state"][0]

    def callback(self, state, **changes):
        return self.client.get(
            SCOPED_CALLBACK_PATH
            + "?"
            + urlencode({"state": state, "code": "fabricated-callback-code"} | changes)
        )

    def test_overview_reads_only_metadata_and_does_not_register_or_read_secrets(self):
        before = list(ConnectorIdentity.objects.values())
        response = self.client.get(self.overview)
        self.assertContains(response, "Bağlantı henüz etkinleştirilmez")
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertNotContains(response, "<script")
        self.assertEqual(list(ConnectorIdentity.objects.values()), before)
        self.assertEqual(Attempt.objects.count(), 0)
        self._client.assert_not_called()
        self._token_path.assert_not_called()
        self._read.assert_not_called()

    def test_both_default_off_switches_deny_every_endpoint_before_io(self):
        for setting in (
            "GOOGLE_ADS_SCOPED_ENDPOINTS_ENABLED",
            "GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED",
        ):
            with override_settings(**{setting: False}):
                for response in (
                    self.client.get(self.overview),
                    self.client.post(self.start_url),
                    self.client.get(SCOPED_CALLBACK_PATH),
                    self.client.post(self.retire_url),
                ):
                    self.assertEqual(response.status_code, 404)
                    self.assertEqual(response["Cache-Control"], "no-store, private")
                    self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
        self._client.assert_not_called()
        self._post.assert_not_called()

    def test_strict_loopback_debug_forwarded_and_configured_owner_guards(self):
        for extra in (
            {"HTTP_HOST": "localhost:8002"},
            {"HTTP_HOST": "127.0.0.1:8003"},
            {"REMOTE_ADDR": "10.0.0.1"},
            {"HTTP_FORWARDED": "for=127.0.0.1"},
            {"HTTP_X_FORWARDED_PROTO": "http"},
        ):
            self.assertEqual(self.client.get(self.overview, **extra).status_code, 404)
        for values in (
            {"DEBUG": True},
            {"GOOGLE_ADS_LOCAL_OAUTH_ENABLED": False},
            {"GOOGLE_ADS_LOCAL_OWNER_ID": "999999"},
            {"GOOGLE_ADS_LOCAL_WORKSPACE_ID": "999999"},
        ):
            with override_settings(**values):
                self.assertEqual(self.client.get(self.overview).status_code, 404)
        self._client.assert_not_called()

    def test_anonymous_callback_never_redirects_to_login_or_echoes_query(self):
        self.client.logout()
        response = self.callback("fabricated-state")
        self.assertEqual(response.status_code, 404)
        self.assertNotIn("Location", response)
        self.assertNotContains(response, "fabricated", status_code=404)
        self._post.assert_not_called()

    def test_post_csrf_required_for_start_and_retire(self):
        client = Client(enforce_csrf_checks=True, HTTP_HOST="127.0.0.1:8002")
        client.force_login(self.owner)
        data = self.form(client=client)
        response = client.post(self.start_url, data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        csrf = client.cookies["csrftoken"].value
        self.assertEqual(
            client.post(self.start_url, data, HTTP_X_CSRFTOKEN=csrf).status_code, 302
        )
        data = self.form("retire_token", client)
        self.assertEqual(client.post(self.retire_url, data).status_code, 403)
        self.assertEqual(
            client.post(self.retire_url, data, HTTP_X_CSRFTOKEN=csrf).status_code, 303
        )
        self._post.assert_not_called()

    def test_only_expected_methods_can_run(self):
        self.assertEqual(self.client.get(self.start_url).status_code, 405)
        self.assertEqual(self.client.get(self.retire_url).status_code, 405)
        self.assertEqual(self.client.post(SCOPED_CALLBACK_PATH).status_code, 405)
        self.assertEqual(Attempt.objects.count(), 0)

    def test_signed_form_confirmation_exact_shape_and_expiry(self):
        data = self.form()
        for invalid in (
            {"token": data["token"]},
            data | {"token": data["token"] + "x"},
            data | {"connection": "fabricated"},
            data | {"confirm": ["yes", "yes"]},
            data | {"token": [data["token"], data["token"]]},
        ):
            self.assertEqual(self.client.post(self.start_url, invalid).status_code, 409)
        with patch("django.core.signing.time.time", return_value=time.time() + 301):
            self.assertEqual(self.client.post(self.start_url, data).status_code, 409)
        self.assertEqual(Attempt.objects.count(), 0)

    def test_other_session_cannot_use_start_ticket(self):
        data = self.form()
        client = Client(HTTP_HOST="127.0.0.1:8002")
        client.force_login(self.owner)
        self.assertEqual(client.post(self.start_url, data).status_code, 409)
        self.assertEqual(Attempt.objects.count(), 0)

    def test_start_replay_changes_nonce_but_not_receipt_or_deadline(self):
        data = self.form()
        first = self.client.post(self.start_url, data)
        before = list(Attempt.objects.values())
        second = self.client.post(self.start_url, data)
        self.assertNotEqual(first.url, second.url)
        self.assertEqual(list(Attempt.objects.values()), before)
        self._post.assert_not_called()

    def test_valid_callback_stores_only_inactive_candidate_and_cleans_url(self):
        state = self.start()
        response = self.callback(state)
        self.assertEqual((response.status_code, response.url), (303, self.overview))
        self.assertEqual(response["Referrer-Policy"], "no-referrer")
        self.assertEqual(Attempt.objects.get().state, "candidate")
        self.assertEqual(
            self._post.call_args.args[1]["redirect_uri"], SCOPED_REDIRECT_URI
        )
        self.assertEqual(ConnectorIdentity.objects.get().state, "quarantined")
        self.assertNotIn("fabricated-callback-code", str(dict(self.client.session)))
        self.assertNotIn(state, str(dict(self.client.session)))
        self.assertContains(self.client.get(self.overview), "Bağlantı etkin değil")

    def test_callback_replay_never_exchanges_twice(self):
        state = self.start()
        self.callback(state)
        self.callback(state)
        self._post.assert_called_once()
        self._write.assert_called_once()

    def test_callback_missing_marker_or_wrong_state_preserves_pending(self):
        self.assertEqual(self.callback("missing").status_code, 303)
        state = self.start()
        self.callback("wrong-state")
        self.assertEqual(Attempt.objects.get().state, "reserved")
        self._post.assert_not_called()
        self.callback(state)
        self.assertEqual(Attempt.objects.get().state, "candidate")

    def test_old_callback_cannot_consume_new_reservation(self):
        old = self.start()
        self.client.post(self.retire_url, self.form("retire_token"))
        new = self.start()
        self.callback(old)
        self.assertEqual(Attempt.objects.filter(state="reserved").count(), 1)
        self._post.assert_not_called()
        self.callback(new)
        self.assertEqual(Attempt.objects.filter(state="candidate").count(), 1)

    def test_rotated_session_marker_cannot_exchange(self):
        state = self.start()
        session = self.client.session
        session.cycle_key()
        self.client.cookies["sessionid"] = session.session_key
        self.callback(state)
        self.assertEqual(Attempt.objects.get().state, "reserved")
        self._post.assert_not_called()
        # Fresh owner session can explicitly retire before exchange; no rebinding.
        self.assertEqual(
            self.client.post(self.retire_url, self.form("retire_token")).status_code,
            303,
        )

    def test_blocked_callback_cannot_exchange(self):
        state = self.start()
        self.block()
        self.callback(state)
        self._post.assert_not_called()
        self.assertEqual(Attempt.objects.get().state, "rejected")

    def test_storage_uncertainty_never_offers_start_or_retire(self):
        state = self.start()
        self._write.side_effect = OSError("fabricated-private-details")
        self.callback(state)
        response = self.client.get(self.overview)
        self.assertContains(response, "İşlem sonucu belirsiz")
        self.assertNotContains(response, "fabricated-private-details")
        self.assertNotIn("start_token", response.context[-1])
        self.assertNotIn("retire_token", response.context[-1])
        self._post.assert_called_once()

    def test_retire_replay_and_wrong_action_cannot_duplicate_or_execute(self):
        start_data = self.form()
        self.start()
        data = self.form("retire_token")
        self.assertEqual(self.client.post(self.retire_url, start_data).status_code, 409)
        for _ in range(2):
            self.assertEqual(self.client.post(self.retire_url, data).status_code, 303)
        self.assertEqual(ConnectorIdentity.objects.get().revision, 1)
        self.assertNotIn(views.MARKER, self.client.session)
        self.assertEqual(Attempt.objects.get().reason, "retired_before_exchange")
        self._post.assert_not_called()

    def test_legacy_grant_presence_blocks_start_without_loading_client(self):
        data = self.form()
        self._token_path.return_value.exists.return_value = True
        self.assertEqual(self.client.post(self.start_url, data).status_code, 503)
        self.assertEqual(Attempt.objects.count(), 0)
        self._client.assert_not_called()

    def test_callback_filter_drops_new_path_and_encoded_queries(self):
        filter_ = OAuthCallbackFilter()
        for message in (
            SCOPED_CALLBACK_PATH + "?code=fabricated",
            SCOPED_CALLBACK_PATH.replace("/", "%2F") + "?code=fabricated",
        ):
            record = logging.LogRecord(
                "django.server", logging.INFO, "", 0, message, (), None
            )
            self.assertFalse(filter_.filter(record))

    def test_store_supports_only_two_fixed_redirects_and_legacy_default_unchanged(self):
        store = LocalAuthorizationStore()
        legacy = store.begin(
            client_id=self.client_value["client_id"], binding=("one", "two", "three")
        )
        self.assertEqual(
            parse_qs(urlsplit(legacy).query)["redirect_uri"], [LOCAL_REDIRECT_URI]
        )
        with self.assertRaises(AuthorizationRejected):
            store.begin(
                client_id=self.client_value["client_id"],
                binding=("one", "two", "three"),
                redirect_uri="https://untrusted.example/callback/",
            )

    def test_slashless_callback_cleans_url_without_query_redirect(self):
        state = self.start()
        response = self.client.get(
            SCOPED_CALLBACK_PATH.rstrip("/")
            + "?"
            + urlencode({"state": state, "code": "fabricated-alias-code"})
        )
        self.assertEqual((response.status_code, response.url), (303, self.overview))
        self.assertEqual(response["Referrer-Policy"], "no-referrer")
        self._post.assert_called_once()

    def test_duplicate_state_does_not_burn_correct_pending_callback(self):
        state = self.start()
        response = self.client.get(
            SCOPED_CALLBACK_PATH
            + "?"
            + urlencode([("state", state), ("state", state), ("code", "fabricated")])
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(Attempt.objects.get().state, "reserved")
        self._post.assert_not_called()
        self.callback(state)
        self._post.assert_called_once()

    def test_generation_change_invalidates_signed_start_before_client_loading(self):
        data = self.form()
        self.rotate()
        self.assertEqual(self.client.post(self.start_url, data).status_code, 409)
        self.assertEqual(Attempt.objects.count(), 0)
        self._client.assert_not_called()

    def test_receipt_changes_between_endpoint_read_and_locked_retirement_deny(self):
        self.start()
        data = self.form("retire_token")
        original = views.retire_reserved

        def retire(**kwargs):
            # Endpoint has read the original receipt; service has not locked yet.
            Attempt.objects.update(client_id_hash="b" * 64)
            return original(**kwargs)

        with patch.object(views, "retire_reserved", side_effect=retire):
            self.assertEqual(self.client.post(self.retire_url, data).status_code, 409)
        self.assertEqual(Attempt.objects.get().state, "reserved")
        self.assertEqual(ConnectorIdentity.objects.get().revision, 0)
        self._post.assert_not_called()

    def test_other_logged_in_session_callback_cannot_exchange(self):
        state = self.start()
        client = Client(HTTP_HOST="127.0.0.1:8002")
        client.force_login(self.owner)
        response = client.get(
            SCOPED_CALLBACK_PATH
            + "?"
            + urlencode({"state": state, "code": "fabricated"})
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(Attempt.objects.get().state, "reserved")
        self._post.assert_not_called()
