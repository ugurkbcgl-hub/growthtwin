"""Focused tests for the synthetic-only policy boundary."""

from dataclasses import replace
from datetime import datetime, timezone

from django.test import SimpleTestCase

from growthtwin.modules.approvals.contracts import (
    SYNTHETIC_POLICY_RULES,
    SYNTHETIC_POLICY_VERSION,
    PolicyReason,
    SyntheticActionEvidence,
    SyntheticEvidenceSource,
    evaluate_synthetic_action,
)


class SyntheticActionPolicyTests(SimpleTestCase):
    def setUp(self):
        self.evidence = SyntheticActionEvidence(
            advertiser_authorized=True,
            destination_authorized=True,
            channel_allowed=True,
            content_approved=True,
            policy_current=True,
            stop_requested=False,
            campaign_cap_minor=500_000,
            account_cap_minor=1_000_000,
            account_committed_minor=200_000,
            requested_minor=100_000,
            currency="TRY",
            action_at=datetime(2026, 10, 5, 12, tzinfo=timezone.utc),
            campaign_starts_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
            campaign_ends_at=datetime(2026, 10, 14, tzinfo=timezone.utc),
            evidence_source=SyntheticEvidenceSource.TEST_FIXTURE,
            evidence_observed_at=datetime(2026, 10, 5, 12, tzinfo=timezone.utc),
        )

    def test_valid_synthetic_evidence_is_only_eligible_for_review(self):
        decision = evaluate_synthetic_action(self.evidence)

        self.assertTrue(decision.eligible_for_synthetic_review)
        self.assertEqual(decision.reasons, ())
        self.assertEqual(decision.evidence_source, self.evidence.evidence_source)
        self.assertEqual(
            decision.evidence_observed_at, self.evidence.evidence_observed_at
        )
        self.assertEqual(decision.policy_version, SYNTHETIC_POLICY_VERSION)
        self.assertEqual(decision.evaluated_rule_ids, SYNTHETIC_POLICY_RULES)
        self.assertFalse(decision.live_dispatch_authorized)

    def test_policy_identifiers_are_reported_even_when_a_check_blocks(self):
        decision = evaluate_synthetic_action(
            replace(self.evidence, advertiser_authorized=None)
        )

        self.assertFalse(decision.eligible_for_synthetic_review)
        self.assertEqual(decision.policy_version, SYNTHETIC_POLICY_VERSION)
        self.assertEqual(decision.evaluated_rule_ids, SYNTHETIC_POLICY_RULES)
        self.assertFalse(decision.live_dispatch_authorized)

    def test_missing_or_unknown_evidence_source_fails_closed(self):
        for source in (None, "live_google_ads"):
            with self.subTest(source=source):
                decision = evaluate_synthetic_action(
                    replace(self.evidence, evidence_source=source)
                )

                self.assertIn(PolicyReason.EVIDENCE_SOURCE_INVALID, decision.reasons)
                self.assertIsNone(decision.evidence_source)
                self.assertFalse(decision.eligible_for_synthetic_review)

    def test_missing_or_naive_observation_time_fails_closed(self):
        cases = (
            (None, PolicyReason.EVIDENCE_TIME_MISSING),
            (datetime(2026, 10, 5, 12), PolicyReason.EVIDENCE_TIME_INVALID),
        )
        for observed_at, expected_reason in cases:
            with self.subTest(observed_at=observed_at):
                decision = evaluate_synthetic_action(
                    replace(self.evidence, evidence_observed_at=observed_at)
                )

                self.assertIn(expected_reason, decision.reasons)
                self.assertIsNone(decision.evidence_observed_at)
                self.assertFalse(decision.eligible_for_synthetic_review)

    def test_observation_time_is_reported_without_a_freshness_claim(self):
        observed_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
        decision = evaluate_synthetic_action(
            replace(self.evidence, evidence_observed_at=observed_at)
        )

        self.assertTrue(decision.eligible_for_synthetic_review)
        self.assertEqual(decision.evidence_observed_at, observed_at)
        self.assertFalse(decision.live_dispatch_authorized)

    def test_unknown_authorization_fails_closed(self):
        decision = evaluate_synthetic_action(
            replace(self.evidence, advertiser_authorized=None)
        )

        self.assertIn(PolicyReason.AUTHORIZATION_MISSING, decision.reasons)
        self.assertFalse(decision.eligible_for_synthetic_review)

    def test_unknown_destination_channel_content_or_policy_fails_closed(self):
        cases = (
            ("destination_authorized", PolicyReason.DESTINATION_MISSING),
            ("channel_allowed", PolicyReason.CHANNEL_NOT_ALLOWED),
            ("content_approved", PolicyReason.CONTENT_NOT_APPROVED),
            ("policy_current", PolicyReason.POLICY_STALE),
        )
        for field, expected_reason in cases:
            with self.subTest(field=field):
                decision = evaluate_synthetic_action(
                    replace(self.evidence, **{field: None})
                )
                self.assertIn(expected_reason, decision.reasons)
                self.assertFalse(decision.eligible_for_synthetic_review)

    def test_unknown_stop_state_fails_closed(self):
        decision = evaluate_synthetic_action(
            replace(self.evidence, stop_requested=None)
        )

        self.assertIn(PolicyReason.STOP_REQUESTED, decision.reasons)

    def test_campaign_and_aggregate_caps_are_checked_separately(self):
        decision = evaluate_synthetic_action(
            replace(
                self.evidence,
                requested_minor=600_000,
                account_committed_minor=500_000,
            )
        )

        self.assertIn(PolicyReason.CAMPAIGN_CAP_EXCEEDED, decision.reasons)
        self.assertIn(PolicyReason.ACCOUNT_CAP_EXCEEDED, decision.reasons)

    def test_missing_budget_fails_closed(self):
        decision = evaluate_synthetic_action(
            replace(self.evidence, account_cap_minor=None)
        )

        self.assertIn(PolicyReason.BUDGET_MISSING, decision.reasons)

    def test_invalid_currency_fails_closed(self):
        decision = evaluate_synthetic_action(replace(self.evidence, currency="try"))

        self.assertIn(PolicyReason.CURRENCY_INVALID, decision.reasons)

    def test_action_outside_flight_fails_closed(self):
        decision = evaluate_synthetic_action(
            replace(
                self.evidence,
                action_at=datetime(2026, 10, 15, tzinfo=timezone.utc),
            )
        )

        self.assertIn(PolicyReason.OUTSIDE_SCHEDULE, decision.reasons)

    def test_naive_timestamp_fails_closed(self):
        decision = evaluate_synthetic_action(
            replace(self.evidence, action_at=datetime(2026, 10, 5, 12))
        )

        self.assertIn(PolicyReason.SCHEDULE_MISSING, decision.reasons)

    def test_non_synthetic_environment_fails_closed(self):
        decision = evaluate_synthetic_action(
            replace(self.evidence, synthetic_environment=False)
        )

        self.assertIn(PolicyReason.LIVE_ENVIRONMENT, decision.reasons)
        self.assertFalse(decision.live_dispatch_authorized)
