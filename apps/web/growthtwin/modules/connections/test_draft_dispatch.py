"""Focused TEST dispatch checks; no real Google requests or credentials."""

import json
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TransactionTestCase, override_settings

from growthtwin.modules.campaigns.google_draft_payload import build_draft_package
from growthtwin.modules.campaigns.models import GoogleDraftApproval, GoogleDraftDispatch

from . import draft_dispatch
from .test_draft_review import DraftReviewTests


@override_settings(GOOGLE_ADS_LOCAL_TEST_CAMPAIGN_ENABLED=True)
class DraftDispatchTests(TransactionTestCase):
    setUp = DraftReviewTests.setUp
    review = DraftReviewTests.review
    submit = DraftReviewTests.submit

    def prepare(self):
        self.assertEqual(self.submit(self.review()).status_code, 302)
        self.package = build_draft_package(self.draft)
        self.binding = (str(self.owner.pk), str(self.workspace.pk), "session")
        self.calls = []
        for name, value in (
            ("verify", "target-key"),
            ("_targets", ("1111111111", "2222222222")),
        ):
            p = patch.object(draft_dispatch.verification, name, return_value=value)
            p.start()
            self.addCleanup(p.stop)
        p = patch.object(draft_dispatch.backend, "_enabled")
        p.start()
        self.addCleanup(p.stop)
        p = patch.object(draft_dispatch, "_request", side_effect=self.remote)
        self.remote_mock = p.start()
        self.addCleanup(p.stop)

    def remote(self, binding, operation, payload):
        self.calls.append(payload)
        if operation == "googleAds:mutate":
            if not payload.get("validateOnly"):
                self.assertEqual(GoogleDraftDispatch.objects.count(), 1)
            return {}
        query = payload["query"]
        if "FROM geo_target_constant" in query:
            return {
                "results": [
                    {
                        "geoTargetConstant": {
                            "resourceName": "geoTargetConstants/123",
                            "name": "Ankara",
                            "countryCode": "TR",
                            "targetType": "City",
                            "status": "ENABLED",
                        }
                    }
                ]
            }
        if "customer.currency_code" in query:
            return {
                "results": [
                    {"customer": {"currencyCode": "TRY", "timeZone": "Europe/Istanbul"}}
                ]
            }
        row = GoogleDraftDispatch.objects.get(draft=self.draft)
        stored = json.loads(row.payload_json)
        if "FROM ad_group_ad" in query:
            return {
                "results": [
                    {
                        "adGroup": {"status": "PAUSED"},
                        "adGroupAd": {
                            "status": "PAUSED",
                            "ad": {
                                "finalUrls": [stored["test_profile"]["test_url"]],
                                "responsiveSearchAd": {
                                    field: [
                                        {"text": x}
                                        for x in stored["package"]["google"][field]
                                    ]
                                    for field in ("headlines", "descriptions")
                                },
                            },
                        },
                    }
                ]
            }
        if "FROM campaign_criterion" in query:
            return {
                "results": [
                    {
                        "campaignCriterion": {
                            "location": {"geoTargetConstant": "geoTargetConstants/123"}
                        }
                    }
                ]
            }
        if "FROM ad_group_criterion" in query:
            return {
                "results": [
                    {
                        "adGroupCriterion": {
                            "status": "PAUSED",
                            "keyword": {
                                "text": "growthtwin synthetic test",
                                "matchType": "EXACT",
                            },
                        }
                    }
                ]
            }
        return {
            "results": [
                {
                    "campaign": {
                        "resourceName": "customers/1111111111/campaigns/123",
                        "name": draft_dispatch._name(row),
                        "status": "PAUSED",
                        "advertisingChannelType": "SEARCH",
                        "geoTargetTypeSetting": {"positiveGeoTargetType": "PRESENCE"},
                        "campaignBudget": "customers/1111111111/campaignBudgets/456",
                        "startDateTime": stored["test_profile"]["start"] + " 00:00:00",
                        "endDateTime": stored["test_profile"]["end"] + " 23:59:59",
                    },
                    "campaignBudget": {
                        "resourceName": "customers/1111111111/campaignBudgets/456",
                        "name": draft_dispatch._name(row),
                        "period": draft_dispatch.budget_spec(stored["test_profile"])[0],
                        draft_dispatch.budget_spec(stored["test_profile"])[
                            1
                        ]: draft_dispatch.budget_spec(stored["test_profile"])[2],
                    },
                }
            ]
        }

    def perform(self, action="create"):
        return draft_dispatch.perform(
            self.binding, self.draft.pk, action, draft_dispatch.review_key(self.package)
        )

    def test_source_assets_paused_and_no_repeat_create(self):
        self.prepare()
        row = self.perform()
        self.assertEqual(row.state, "paused")
        self.perform()
        self.assertEqual(self.perform("stop").state, "stopped")
        creates = [
            p
            for p in self.calls
            if "mutateOperations" in p
            and not p.get("validateOnly")
            and "campaignBudgetOperation" in p["mutateOperations"][0]
        ]
        self.assertEqual(len(creates), 1)
        operations = creates[0]["mutateOperations"]
        budget = operations[0]["campaignBudgetOperation"]["create"]
        self.assertEqual(budget["period"], "CUSTOM_PERIOD")
        self.assertEqual(
            budget["totalAmountMicros"], str(self.draft.media_budget_minor * 10000)
        )
        self.assertNotIn("amountMicros", budget)
        self.assertFalse(creates[0]["partialFailure"])
        for item in operations:
            value = next(iter(item.values()))["create"]
            if "status" in value:
                self.assertEqual(value["status"], "PAUSED")
        ad = operations[4]["adGroupAdOperation"]["create"]["ad"]
        self.assertEqual(
            ad["responsiveSearchAd"]["headlines"][0]["text"],
            json.loads(self.package.payload_json)["google"]["headlines"][0],
        )
        self.assertEqual(ad["finalUrls"], ["https://example.com/"])
        self.assertEqual(
            GoogleDraftApproval.objects.get().payload_json, self.package.payload_json
        )

    def test_timeout_is_committed_and_never_resent(self):
        self.prepare()
        original = self.remote

        def timeout(binding, operation, payload):
            if operation == "googleAds:mutate" and not payload.get("validateOnly"):
                self.calls.append(payload)
                raise TimeoutError("sensitive response")
            return original(binding, operation, payload)

        self.remote_mock.side_effect = timeout
        self.assertEqual(self.perform().state, "uncertain")
        self.assertEqual(self.perform().state, "paused")
        self.assertEqual(
            sum(
                "mutateOperations" in p and not p.get("validateOnly")
                for p in self.calls
            ),
            1,
        )

    def test_stale_source_blocks_create_but_does_not_block_stop(self):
        self.prepare()
        self.draft.media_budget_minor += 1
        self.draft.save(update_fields=["media_budget_minor"])
        with self.assertRaises(GoogleDraftApproval.DoesNotExist):
            self.perform()
        self.assertEqual(GoogleDraftDispatch.objects.count(), 0)
        self.draft.media_budget_minor -= 1
        self.draft.save(update_fields=["media_budget_minor"])
        self.perform()
        self.draft.preferred_creative_key = ""
        self.draft.save(update_fields=["preferred_creative_key"])
        self.assertEqual(self.perform("stop").state, "stopped")
        response = self.client.get(
            "/connections/google/draft-status/",
            {"draft": self.draft.pk},
            HTTP_HOST="127.0.0.1:8002",
        )
        self.assertContains(response, "Durdur ve doğrula")

    def test_wrong_test_profile_rejected_before_intent(self):
        self.prepare()
        with self.assertRaises(ValidationError):
            draft_dispatch.perform(self.binding, self.draft.pk, "create", "old-key")
        self.assertEqual(GoogleDraftDispatch.objects.count(), 0)

    def test_http_missing_confirmation_csrf_and_get_never_dispatch(self):
        self.prepare()
        data = self.review()
        data["action"] = "create"
        data.pop("confirm")
        response = self.client.post(
            "/connections/google/draft-dispatch/",
            data,
            HTTP_HOST="127.0.0.1:8002",
            HTTP_ORIGIN="http://127.0.0.1:8002",
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            self.client.get(
                "/connections/google/draft-dispatch/", HTTP_HOST="127.0.0.1:8002"
            ).status_code,
            405,
        )
        data.pop("csrfmiddlewaretoken")
        self.assertEqual(
            self.client.post(
                "/connections/google/draft-dispatch/", data, HTTP_HOST="127.0.0.1:8002"
            ).status_code,
            403,
        )
        self.remote_mock.assert_not_called()

    def test_wrong_currency_or_ambiguous_geo_never_creates(self):
        self.prepare()
        self.remote_mock.return_value = {}
        self.remote_mock.side_effect = lambda binding, operation, payload: {
            "results": []
        }
        with self.assertRaises(ValueError):
            self.perform()
        self.assertEqual(GoogleDraftDispatch.objects.count(), 0)

    def test_wrong_currency_blocks_before_validation(self):
        self.prepare()
        original = self.remote

        def wrong(binding, operation, payload):
            if "customer.currency_code" in payload.get("query", ""):
                return {
                    "results": [
                        {
                            "customer": {
                                "currencyCode": "USD",
                                "timeZone": "Europe/Istanbul",
                            }
                        }
                    ]
                }
            return original(binding, operation, payload)

        self.remote_mock.side_effect = wrong
        with self.assertRaises(ValueError):
            self.perform()
        self.assertEqual(GoogleDraftDispatch.objects.count(), 0)

    def test_edit_during_final_verification_commits_intent_but_never_writes(self):
        self.prepare()
        calls = []

        def verify(binding):
            calls.append(1)
            if len(calls) == 2:
                self.draft.media_budget_minor += 1
                self.draft.save(update_fields=["media_budget_minor"])
            return "target-key"

        with patch.object(draft_dispatch.verification, "verify", side_effect=verify):
            self.assertEqual(self.perform().state, "uncertain")
        self.assertEqual(GoogleDraftDispatch.objects.count(), 1)
        self.assertFalse(
            any(
                "mutateOperations" in p and not p.get("validateOnly")
                for p in self.calls
            )
        )

    def test_remote_drift_is_uncertain_but_pause_still_sent(self):
        self.prepare()
        self.perform()
        original = self.remote

        def drift(binding, operation, payload):
            result = original(binding, operation, payload)
            if "FROM campaign WHERE" in payload.get("query", ""):
                result["results"][0]["campaignBudget"]["amountMicros"] = "9990000"
            return result

        self.remote_mock.side_effect = drift
        self.assertEqual(self.perform("read").state, "uncertain")
        self.assertEqual(self.perform("stop").state, "uncertain")
        self.assertTrue(
            any(
                "mutateOperations" in p
                and "update" in p["mutateOperations"][0].get("campaignOperation", {})
                for p in self.calls
            )
        )

    def test_legacy_daily_ledger_read_stop_and_no_conversion(self):
        self.prepare()
        from uuid import uuid4

        legacy = draft_dispatch.profile(self.package)
        legacy.update(version="workspace-paused-test-v1", daily_micros="333330000")
        legacy.pop("period")
        legacy.pop("total_micros")
        row = GoogleDraftDispatch.objects.create(
            draft=self.draft,
            approval=GoogleDraftApproval.objects.get(),
            operation_id=uuid4(),
            configuration_key="target-key",
            payload_json=json.dumps(
                {
                    "package": json.loads(self.package.payload_json),
                    "test_profile": legacy,
                    "geo_resource": "geoTargetConstants/123",
                }
            ),
        )
        original = row.payload_json
        self.assertEqual(self.perform("read").state, "paused")
        with self.assertRaises(ValidationError):
            self.perform("create")
        self.assertEqual(self.perform("stop").state, "stopped")
        row.refresh_from_db()
        self.assertEqual(row.payload_json, original)
        response = self.client.get(
            "/connections/google/draft-review/",
            {"draft": self.draft.pk},
            HTTP_HOST="127.0.0.1:8002",
        )
        self.assertContains(response, "günlük ortalama")
        self.assertContains(response, 'value="create" disabled')
        self.assertFalse(
            any(
                "mutateOperations" in p
                and "campaignBudgetOperation" in p["mutateOperations"][0]
                for p in self.calls
            )
        )

    def test_wrong_total_period_or_amount_never_reports_verified(self):
        self.prepare()
        self.perform()
        original = self.remote
        for field, value in (("period", "DAILY"), ("totalAmountMicros", "9990000")):

            def drift(binding, operation, payload):
                result = original(binding, operation, payload)
                if "FROM campaign WHERE" in payload.get("query", ""):
                    result["results"][0]["campaignBudget"][field] = value
                return result

            self.remote_mock.side_effect = drift
            self.assertEqual(self.perform("read").state, "uncertain")

    def test_unknown_budget_version_fails_closed(self):
        with self.assertRaises(ValidationError):
            draft_dispatch.budget_spec({"version": "unknown"})
