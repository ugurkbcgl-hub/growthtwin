"""Durable test intent survives uncertain remote results without duplicate writes."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError
from django.test import TransactionTestCase, override_settings

from growthtwin.modules.campaigns.models import GoogleTestCampaign
from growthtwin.modules.workspaces.models import Workspace

from . import backend, test_campaign


@override_settings(GOOGLE_ADS_LOCAL_TEST_CAMPAIGN_ENABLED=True)
class TestCampaignLifecycleTests(TransactionTestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="test-owner")
        self.workspace = Workspace.objects.create(owner=self.owner, name="Synthetic")
        self.binding = (str(self.owner.pk), str(self.workspace.pk), "session")
        for name, value in (("_enabled", None), ("_token_path", None)):
            patcher = patch.object(backend, name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        for name, value in (
            ("configuration_key", "key"),
            ("verify", "key"),
            ("_targets", ("1111111111", "2222222222")),
        ):
            patcher = patch.object(test_campaign.verification, name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.calls = []

    def response(self, binding, operation, payload):
        self.calls.append((operation, payload))
        if operation == "googleAds:mutate":
            if not payload.get("validateOnly"):
                self.assertEqual(GoogleTestCampaign.objects.count(), 1)
            return {}
        row = GoogleTestCampaign.objects.get(workspace=self.workspace)
        return {
            "results": [
                {
                    "campaign": {
                        "campaignBudget": "customers/1111111111/campaignBudgets/456",
                        "resourceName": "customers/1111111111/campaigns/123",
                        "name": test_campaign._name(row),
                        "status": "PAUSED",
                        "advertisingChannelType": "SEARCH",
                    },
                    "campaignBudget": {
                        "resourceName": "customers/1111111111/campaignBudgets/456",
                        "name": test_campaign._name(row) + " budget",
                        "amountMicros": "1000000",
                    },
                }
            ]
        }

    def test_create_read_repeat_stop_never_creates_twice(self):
        with patch.object(test_campaign, "_request", side_effect=self.response):
            row = test_campaign.perform(self.binding, "create")
            self.assertEqual(row.observed_status, "PAUSED")
            test_campaign.perform(self.binding, "create")
            test_campaign.perform(self.binding, "read")
            row = test_campaign.perform(self.binding, "stop")
            self.assertEqual(row.observed_status, "PAUSED")
        creates = [
            p
            for op, p in self.calls
            if op == "googleAds:mutate"
            and not p.get("validateOnly")
            and "campaignBudgetOperation" in p["mutateOperations"][0]
        ]
        self.assertEqual(len(creates), 1)
        self.assertFalse(creates[0]["partialFailure"])
        for item in creates[0]["mutateOperations"]:
            create = next(iter(item.values()))["create"]
            if "status" in create:
                self.assertEqual(create["status"], "PAUSED")
        with self.assertRaises(ProtectedError):
            self.workspace.delete()

    def test_timeout_intent_prevents_create_after_restart(self):
        def uncertain(binding, operation, payload):
            self.calls.append((operation, payload))
            if operation == "googleAds:mutate" and not payload.get("validateOnly"):
                raise TimeoutError("private")
            return {"results": []}

        with patch.object(test_campaign, "_request", side_effect=uncertain):
            row = test_campaign.perform(self.binding, "create")
            self.assertEqual(row.state, "uncertain")
            test_campaign.perform(self.binding, "create")
        actual = [
            p
            for op, p in self.calls
            if op == "googleAds:mutate" and not p.get("validateOnly")
        ]
        self.assertEqual(len(actual), 1)
        self.assertEqual(GoogleTestCampaign.objects.count(), 1)

    def test_failed_test_verification_prevents_any_mutation(self):
        with (
            patch.object(
                test_campaign.verification,
                "verify",
                side_effect=backend.ConnectionUnavailable(),
            ),
            patch.object(test_campaign, "_request") as request,
        ):
            with self.assertRaises(backend.ConnectionUnavailable):
                test_campaign.perform(self.binding, "create")
            request.assert_not_called()
        self.assertEqual(GoogleTestCampaign.objects.count(), 0)

    def test_google_nonshared_budget_name_is_accepted_only_with_linked_resource(self):
        def canonical(binding, operation, payload):
            result = self.response(binding, operation, payload)
            if operation == "googleAds:search":
                result["results"][0]["campaignBudget"]["name"] = result["results"][0][
                    "campaign"
                ]["name"]
            return result

        with patch.object(test_campaign, "_request", side_effect=canonical):
            row = test_campaign.perform(self.binding, "create")
            self.assertEqual(row.state, "paused")

        def wrong_budget(binding, operation, payload):
            result = canonical(binding, operation, payload)
            if operation == "googleAds:search":
                result["results"][0]["campaignBudget"]["resourceName"] = (
                    "customers/1111111111/campaignBudgets/999"
                )
            return result

        with patch.object(test_campaign, "_request", side_effect=wrong_budget):
            row = test_campaign.perform(self.binding, "read")
            self.assertEqual(row.state, "uncertain")

    def test_validation_failure_does_not_reserve_or_send_actual_create(self):
        with patch.object(
            test_campaign,
            "_request",
            side_effect=test_campaign.TestCampaignRejected("REQUIRED"),
        ) as request:
            with self.assertRaises(backend.ConnectionUnavailable):
                test_campaign.perform(self.binding, "create")
            self.assertEqual(request.call_count, 1)
            self.assertTrue(request.call_args.args[2]["validateOnly"])
        self.assertEqual(GoogleTestCampaign.objects.count(), 0)
