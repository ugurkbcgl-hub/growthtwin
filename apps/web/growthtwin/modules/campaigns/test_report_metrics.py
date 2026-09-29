"""Validation for the provider-neutral campaign reporting contract."""

from datetime import date, datetime, timezone
from decimal import Decimal

from django.test import SimpleTestCase

from growthtwin.modules.campaigns.report_metrics import (
    CampaignReportMetric,
    MetricStatus,
    MetricUnavailableReason,
    MetricUnit,
    ReportingWindow,
)


class CampaignReportMetricTests(SimpleTestCase):
    def setUp(self):
        self.window = ReportingWindow(date(2026, 9, 1), date(2026, 9, 30))

    def test_available_zero_is_distinct_from_unavailable(self):
        observed_zero = CampaignReportMetric(
            key="clicks",
            label="Clicks",
            status=MetricStatus.AVAILABLE,
            unit=MetricUnit.COUNT,
            window=self.window,
            value=0,
            source="synthetic-report-fixture",
            observed_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
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
            observed_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
        )

        self.assertEqual(metric.currency, "TRY")
        self.assertEqual(metric.source, "synthetic-report-fixture")
        self.assertEqual(metric.observed_at.utcoffset().total_seconds(), 0)

    def test_available_metric_requires_value_source_and_aware_observation(self):
        required = {
            "key": "impressions",
            "label": "Impressions",
            "status": MetricStatus.AVAILABLE,
            "unit": MetricUnit.COUNT,
            "window": self.window,
            "value": 3,
            "source": "fixture",
            "observed_at": datetime(2026, 10, 1, tzinfo=timezone.utc),
        }
        for field, value in (
            ("value", None),
            ("source", None),
            ("observed_at", datetime(2026, 10, 1)),
            ("observed_at", "2026-10-01T00:00:00Z"),
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                CampaignReportMetric(**(required | {field: value}))

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
                    "observed_at": datetime(2026, 10, 1, tzinfo=timezone.utc),
                },
                "Dönem verisi kısmi",
            ),
            (
                MetricUnavailableReason.STALE,
                {
                    "source": "google-ads",
                    "observed_at": datetime(2026, 10, 1, tzinfo=timezone.utc),
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
            "observed_at": datetime(2026, 10, 1, tzinfo=timezone.utc),
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
                observed_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
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
            "observed_at": datetime(2026, 10, 1, tzinfo=timezone.utc),
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
