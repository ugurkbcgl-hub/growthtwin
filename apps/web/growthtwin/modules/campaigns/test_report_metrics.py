"""Validation for the provider-neutral campaign reporting contract."""

from datetime import date, datetime, timezone
from decimal import Decimal

from django.test import SimpleTestCase

from growthtwin.modules.campaigns.report_metrics import (
    CampaignReportMetric,
    MetricFreshness,
    MetricObservation,
    MetricStatus,
    MetricUnavailableReason,
    MetricUnit,
    ReportingWindow,
)


class CampaignReportMetricTests(SimpleTestCase):
    def setUp(self):
        self.window = ReportingWindow(date(2026, 9, 1), date(2026, 9, 30))

    def observation(self, **overrides):
        values = {
            "scope": "synthetic-campaign-1",
            "requested_window": self.window,
            "covered_window": self.window,
            "retrieved_at": datetime(2026, 10, 1, tzinfo=timezone.utc),
            "response_complete": True,
            "row_present": True,
            "freshness": MetricFreshness.CURRENT,
            "freshness_rule": "synthetic-freshness-rule-v1",
        }
        return MetricObservation(**(values | overrides))

    def test_available_zero_is_distinct_from_unavailable(self):
        observed_zero = CampaignReportMetric(
            key="clicks",
            label="Clicks",
            status=MetricStatus.AVAILABLE,
            unit=MetricUnit.COUNT,
            window=self.window,
            value=0,
            source="synthetic-report-fixture",
            observation=self.observation(),
        )
        no_data = CampaignReportMetric(
            key="clicks",
            label="Clicks",
            status=MetricStatus.UNAVAILABLE,
            unit=MetricUnit.COUNT,
            window=self.window,
            unavailable_reason=MetricUnavailableReason.NOT_CONNECTED,
        )

        self.assertEqual(observed_zero.value, 0)
        self.assertEqual(observed_zero.status, MetricStatus.AVAILABLE)
        self.assertIsNone(no_data.value)
        self.assertEqual(no_data.status, MetricStatus.UNAVAILABLE)

    def test_currency_metric_records_currency_and_observation_provenance(self):
        metric = CampaignReportMetric(
            key="media_spend",
            label="Media spend",
            status=MetricStatus.AVAILABLE,
            unit=MetricUnit.CURRENCY,
            window=self.window,
            value=Decimal("0.00"),
            currency="TRY",
            source="synthetic-report-fixture",
            observation=self.observation(),
        )

        self.assertEqual(metric.currency, "TRY")
        self.assertEqual(metric.source, "synthetic-report-fixture")
        self.assertEqual(metric.observation.retrieved_at.utcoffset().total_seconds(), 0)

    def test_available_metric_requires_value_source_and_complete_fresh_observation(
        self,
    ):
        required = {
            "key": "impressions",
            "label": "Impressions",
            "status": MetricStatus.AVAILABLE,
            "unit": MetricUnit.COUNT,
            "window": self.window,
            "value": 3,
            "source": "fixture",
            "observation": self.observation(),
        }
        for field, value in (
            ("value", None),
            ("source", None),
            ("observation", None),
            ("observation", "2026-10-01T00:00:00Z"),
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                CampaignReportMetric(**(required | {field: value}))

    def test_available_zero_requires_complete_exact_window_and_present_row(self):
        required = {
            "key": "clicks",
            "label": "Clicks",
            "status": MetricStatus.AVAILABLE,
            "unit": MetricUnit.COUNT,
            "window": self.window,
            "value": 0,
            "source": "synthetic-report-fixture",
        }
        observations = (
            self.observation(row_present=False),
            self.observation(response_complete=False),
            self.observation(
                covered_window=ReportingWindow(date(2026, 9, 1), date(2026, 9, 29))
            ),
            self.observation(
                requested_window=ReportingWindow(date(2026, 9, 2), date(2026, 9, 30)),
                covered_window=ReportingWindow(date(2026, 9, 2), date(2026, 9, 30)),
            ),
        )
        for observation in observations:
            with self.subTest(observation=observation), self.assertRaises(ValueError):
                CampaignReportMetric(**(required | {"observation": observation}))

    def test_retrieval_time_alone_does_not_confirm_a_metric_row(self):
        observation = self.observation(
            covered_window=None,
            row_present=False,
            freshness=MetricFreshness.UNKNOWN,
            freshness_rule=None,
        )
        self.assertEqual(
            observation.retrieved_at, datetime(2026, 10, 1, tzinfo=timezone.utc)
        )
        self.assertFalse(observation.is_complete_for(self.window))

    def test_recent_retrieval_with_unknown_freshness_cannot_be_available(self):
        with self.assertRaises(ValueError):
            CampaignReportMetric(
                key="clicks",
                label="Clicks",
                status=MetricStatus.AVAILABLE,
                unit=MetricUnit.COUNT,
                window=self.window,
                value=0,
                source="synthetic-report-fixture",
                observation=self.observation(
                    freshness=MetricFreshness.UNKNOWN,
                    freshness_rule=None,
                ),
            )

    def test_stale_unavailable_reason_requires_source_rule_classification(self):
        with self.assertRaises(ValueError):
            CampaignReportMetric(
                key="clicks",
                label="Clicks",
                status=MetricStatus.UNAVAILABLE,
                unit=MetricUnit.COUNT,
                window=self.window,
                unavailable_reason=MetricUnavailableReason.STALE,
                source="synthetic-report-fixture",
                observation=self.observation(),
            )

    def test_observation_requires_valid_scope_time_and_covered_window(self):
        invalid = (
            {"scope": " "},
            {"retrieved_at": datetime(2026, 10, 1)},
            {"response_complete": None},
            {"row_present": 0},
            {"freshness": None},
            {"freshness_rule": 12},
            {"freshness": MetricFreshness.CURRENT, "freshness_rule": None},
            {"covered_window": ReportingWindow(date(2026, 8, 31), date(2026, 9, 1))},
        )
        for overrides in invalid:
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                self.observation(**overrides)

    def test_unavailable_metric_rejects_numeric_value_or_provenance(self):
        required = {
            "key": "clicks",
            "label": "Clicks",
            "status": MetricStatus.UNAVAILABLE,
            "unit": MetricUnit.COUNT,
            "window": self.window,
            "unavailable_reason": MetricUnavailableReason.NOT_CONNECTED,
        }
        for field, value in (("value", 0), ("source", "fixture")):
            with self.subTest(field=field), self.assertRaises(ValueError):
                CampaignReportMetric(**(required | {field: value}))

    def test_unavailable_reasons_have_specific_provenance_requirements(self):
        required = {
            "key": "reach",
            "label": "Reach",
            "status": MetricStatus.UNAVAILABLE,
            "unit": MetricUnit.COUNT,
            "window": self.window,
        }
        cases = (
            (
                MetricUnavailableReason.UNSUPPORTED,
                {"source": "google-ads"},
                "Bu kanal bu metriği desteklemiyor",
            ),
            (
                MetricUnavailableReason.PARTIAL,
                {
                    "source": "google-ads",
                    "observation": self.observation(
                        covered_window=ReportingWindow(
                            date(2026, 9, 1), date(2026, 9, 29)
                        )
                    ),
                },
                "Dönem verisi kısmi",
            ),
            (
                MetricUnavailableReason.STALE,
                {
                    "source": "google-ads",
                    "observation": self.observation(
                        freshness=MetricFreshness.STALE,
                        freshness_rule="synthetic-stale-rule-v1",
                    ),
                },
                "Kaynak verisi güncel değil",
            ),
        )
        for reason, provenance, message in cases:
            with self.subTest(reason=reason):
                metric = CampaignReportMetric(
                    **(required | {"unavailable_reason": reason} | provenance)
                )
                self.assertIsNone(metric.value)
                self.assertEqual(metric.unavailable_message, message)

    def test_partial_or_stale_metric_requires_window_source_and_observation_time(self):
        required = {
            "key": "clicks",
            "label": "Clicks",
            "status": MetricStatus.UNAVAILABLE,
            "unit": MetricUnit.COUNT,
            "window": None,
            "unavailable_reason": MetricUnavailableReason.PARTIAL,
            "source": "google-ads",
            "observation": self.observation(
                covered_window=ReportingWindow(date(2026, 9, 1), date(2026, 9, 29))
            ),
        }
        with self.assertRaises(ValueError):
            CampaignReportMetric(**required)

    def test_available_metric_cannot_have_unavailable_reason(self):
        with self.assertRaises(ValueError):
            CampaignReportMetric(
                key="clicks",
                label="Clicks",
                status=MetricStatus.AVAILABLE,
                unit=MetricUnit.COUNT,
                window=self.window,
                value=0,
                source="fixture",
                observation=self.observation(),
                unavailable_reason=MetricUnavailableReason.NOT_CONNECTED,
            )

    def test_invalid_values_and_currency_are_rejected(self):
        required = {
            "key": "clicks",
            "label": "Clicks",
            "status": MetricStatus.AVAILABLE,
            "unit": MetricUnit.COUNT,
            "window": self.window,
            "value": 1,
            "source": "fixture",
            "observation": self.observation(),
        }
        for overrides in (
            {"value": -1},
            {"value": True},
            {"value": Decimal("NaN")},
            {"currency": "TRY"},
        ):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                CampaignReportMetric(**(required | overrides))

        for currency in (None, "try", "US", "US1"):
            with self.subTest(currency=currency), self.assertRaises(ValueError):
                CampaignReportMetric(
                    **(
                        required
                        | {
                            "unit": MetricUnit.CURRENCY,
                            "currency": currency,
                        }
                    )
                )

    def test_reporting_window_rejects_reversed_dates(self):
        with self.assertRaises(ValueError):
            ReportingWindow(date(2026, 9, 30), date(2026, 9, 1))
