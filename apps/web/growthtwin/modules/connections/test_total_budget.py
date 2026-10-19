"""Total budget validation never falls back to daily or creates a resource."""

from unittest.mock import patch

from django.core import signing
from django.core.exceptions import ValidationError
from django.test import TransactionTestCase, override_settings

from growthtwin.modules.campaigns.models import GoogleDraftApproval, GoogleDraftDispatch

from . import backend, draft_dispatch, total_budget
from . import test_draft_dispatch as dispatch_helpers
from . import test_draft_review as review_helpers
from .draft_review import SALT


@override_settings(GOOGLE_ADS_LOCAL_TEST_CAMPAIGN_ENABLED=True)
class TotalBudgetTests(TransactionTestCase):
    setUp = review_helpers.DraftReviewTests.setUp
    review = review_helpers.DraftReviewTests.review
    submit = review_helpers.DraftReviewTests.submit
    prepare = dispatch_helpers.DraftDispatchTests.prepare
    remote = dispatch_helpers.DraftDispatchTests.remote
    perform = dispatch_helpers.DraftDispatchTests.perform

    def validate(self):
        return total_budget.validate(
            self.binding, self.draft.pk, total_budget.review_key(self.package)
        )

    def data(self):
        data = self.review()
        data["review"] = signing.dumps(
            {
                "owner": self.binding[0],
                "workspace": self.binding[1],
                "draft": self.draft.pk,
                "target_key": "target-key",
                "budget_key": total_budget.review_key(self.package),
            },
            salt=SALT + "-total-budget",
        )
        return data

    def post(self, data):
        return self.client.post(
            "/connections/google/total-budget-validate/",
            data,
            HTTP_HOST="127.0.0.1:8002",
            HTTP_ORIGIN="http://127.0.0.1:8002",
        )

    def test_exact_total_and_validate_only_no_ledger(self):
        self.prepare()
        original = GoogleDraftApproval.objects.get().payload_json
        result = self.validate()
        self.assertEqual(
            result["total_micros"], str(self.draft.media_budget_minor * 10000)
        )
        mutations = [p for p in self.calls if "mutateOperations" in p]
        self.assertEqual(len(mutations), 1)
        payload = mutations[0]
        self.assertIs(payload["validateOnly"], True)
        self.assertIs(payload["partialFailure"], False)
        budget = payload["mutateOperations"][0]["campaignBudgetOperation"]["create"]
        self.assertEqual(budget["period"], "CUSTOM_PERIOD")
        self.assertEqual(budget["totalAmountMicros"], result["total_micros"])
        self.assertNotIn("amountMicros", budget)
        self.assertFalse(budget["explicitlyShared"])
        for operation in payload["mutateOperations"]:
            value = next(iter(operation.values()))["create"]
            if "status" in value:
                self.assertEqual(value["status"], "PAUSED")
        self.assertEqual(GoogleDraftDispatch.objects.count(), 0)
        self.assertEqual(GoogleDraftApproval.objects.get().payload_json, original)

    def test_rejection_or_timeout_never_falls_back(self):
        self.prepare()
        original = self.remote

        def rejected(binding, operation, payload):
            if operation == "googleAds:mutate":
                self.calls.append(payload)
                raise backend.ConnectionUnavailable("private response suppressed")
            return original(binding, operation, payload)

        self.remote_mock.side_effect = rejected
        with self.assertRaises(backend.ConnectionUnavailable):
            self.validate()
        self.assertEqual(sum("mutateOperations" in p for p in self.calls), 1)
        self.assertEqual(GoogleDraftDispatch.objects.count(), 0)

    def test_existing_daily_ledger_untouched(self):
        self.prepare()
        self.perform()
        row = GoogleDraftDispatch.objects.get()
        before = (
            row.payload_json,
            row.operation_id,
            row.resource_name,
            row.state,
            row.updated_at,
        )
        self.validate()
        row.refresh_from_db()
        self.assertEqual(
            before,
            (
                row.payload_json,
                row.operation_id,
                row.resource_name,
                row.state,
                row.updated_at,
            ),
        )

    def test_source_or_target_change_during_lookup_blocks_request(self):
        self.prepare()

        def changed(binding):
            self.draft.media_budget_minor += 1
            self.draft.save(update_fields=["media_budget_minor"])
            return "geoTargetConstants/123"

        with patch.object(draft_dispatch, "_resolve", side_effect=changed):
            with self.assertRaises(GoogleDraftApproval.DoesNotExist):
                self.validate()
        self.assertFalse(any("mutateOperations" in p for p in self.calls))

    def test_stale_key_and_unverified_test_target_block(self):
        self.prepare()
        with self.assertRaises(ValidationError):
            total_budget.validate(self.binding, self.draft.pk, "old-key")
        with patch.object(
            draft_dispatch.verification, "verify", return_value="other-target"
        ):
            with self.assertRaises(backend.ConnectionUnavailable):
                self.validate()
        self.remote_mock.assert_not_called()

    def test_http_signed_review_csrf_and_no_get(self):
        self.prepare()
        data = self.data()
        self.assertContains(self.post(data), "yeni reklam veya bütçe oluşturulmadı")
        data["review"] += "tampered"
        self.assertEqual(self.post(data).status_code, 409)
        data.pop("csrfmiddlewaretoken")
        self.assertEqual(self.post(data).status_code, 403)
        self.assertEqual(
            self.client.get(
                "/connections/google/total-budget-validate/", HTTP_HOST="127.0.0.1:8002"
            ).status_code,
            405,
        )

    def test_get_review_is_provider_free_and_feature_off_blocks(self):
        self.prepare()
        self.review()
        self.remote_mock.assert_not_called()
        with override_settings(GOOGLE_ADS_LOCAL_TEST_CAMPAIGN_ENABLED=False):
            with self.assertRaises(backend.ConnectionUnavailable):
                self.validate()
        self.remote_mock.assert_not_called()

    def test_http_timeout_and_malformed_response_are_sanitized(self):
        self.prepare()
        data = self.data()
        for error in (
            TimeoutError("private provider details"),
            KeyError("private account"),
            AttributeError("private malformed object"),
            IndexError("private empty list"),
        ):
            with patch.object(draft_dispatch, "_resolve", side_effect=error):
                response = self.post(data)
                self.assertEqual(response.status_code, 409)
                self.assertNotIn(b"private", response.content)
        self.assertEqual(GoogleDraftDispatch.objects.count(), 0)
