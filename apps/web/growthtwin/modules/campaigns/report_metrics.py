"""Provider-neutral values for campaign report metrics."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import StrEnum


class MetricStatus(StrEnum):
    """Whether a metric contains an observed value or is not available."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class MetricUnavailableReason(StrEnum):
    """Why an unavailable metric must not be interpreted as zero."""

    NOT_CONNECTED = "not_connected"
    UNSUPPORTED = "unsupported"
    PARTIAL = "partial"
    STALE = "stale"
    FRESHNESS_UNKNOWN = "freshness_unknown"


class MetricUnit(StrEnum):
    """Supported measurement kinds for the first reporting contract."""

    COUNT = "count"
    CURRENCY = "currency"


class MetricFreshness(StrEnum):
    """Freshness classification evaluated under a source-specific rule."""

    CURRENT = "current"
    STALE = "stale"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class MetricFreshnessRule:
    """Configured freshness policy for one source and metric family.

    The interval is an application policy, not a provider guarantee or SLO.
    """

    identifier: str
    source: str
    metric_family: str
    max_age: timedelta

    def __post_init__(self):
        for name in ("identifier", "source", "metric_family"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Freshness rule {name} is required.")
        if not isinstance(self.max_age, timedelta) or self.max_age <= timedelta(0):
            raise ValueError("Freshness rule max age must be a positive duration.")


def classify_metric_freshness(
    *,
    source_data_as_of: datetime | None,
    checked_at: datetime,
    rule: MetricFreshnessRule | None,
) -> MetricFreshness:
    """Classify source data time under an explicit configured rule.

    Missing evidence or a source timestamp in the future is unknown. Retrieval
    time is intentionally not an input: a recent fetch can contain old data.
    """

    for name, value in (
        ("checked_at", checked_at),
        ("source_data_as_of", source_data_as_of),
    ):
        if value is not None and (
            not isinstance(value, datetime) or value.utcoffset() is None
        ):
            raise ValueError(f"{name} must be timezone-aware.")
    if rule is not None and not isinstance(rule, MetricFreshnessRule):
        raise ValueError("Freshness rule must use the configured rule type.")
    if source_data_as_of is None or rule is None:
        return MetricFreshness.UNKNOWN
    age = checked_at - source_data_as_of
    if age < timedelta(0):
        return MetricFreshness.UNKNOWN
    return MetricFreshness.CURRENT if age <= rule.max_age else MetricFreshness.STALE


@dataclass(frozen=True)
class ReportingWindow:
    """Inclusive dates covered by a report metric."""

    start: date
    end: date

    def __post_init__(self):
        if self.start > self.end:
            raise ValueError("Reporting window end must not precede its start.")


@dataclass(frozen=True)
class MetricObservation:
    """Synthetic evidence about report retrieval and metric-period coverage.

    ``retrieved_at`` records when the result was fetched. It does not establish
    freshness by itself. A metric is complete only when the requested period
    was covered, the response/pagination finished, and a row for the metric was
    actually present.
    """

    scope: str
    source: str
    metric_family: str
    requested_window: ReportingWindow
    covered_window: ReportingWindow | None
    retrieved_at: datetime
    source_data_as_of: datetime | None
    freshness_checked_at: datetime
    response_complete: bool
    row_present: bool
    freshness: MetricFreshness
    freshness_rule: MetricFreshnessRule | None

    def __post_init__(self):
        if not isinstance(self.scope, str) or not self.scope.strip():
            raise ValueError("Observation scope is required.")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("Observation source is required.")
        if not isinstance(self.metric_family, str) or not self.metric_family.strip():
            raise ValueError("Observation metric family is required.")
        if not isinstance(self.requested_window, ReportingWindow):
            raise ValueError("Observation requires a requested reporting window.")
        if self.covered_window is not None and not isinstance(
            self.covered_window, ReportingWindow
        ):
            raise ValueError("Covered window must use the report window type.")
        if self.covered_window is not None and (
            self.covered_window.start < self.requested_window.start
            or self.covered_window.end > self.requested_window.end
        ):
            raise ValueError("Covered window must be inside the requested window.")
        if (
            not isinstance(self.retrieved_at, datetime)
            or self.retrieved_at.utcoffset() is None
        ):
            raise ValueError("Retrieval time must be timezone-aware.")
        if (
            not isinstance(self.freshness_checked_at, datetime)
            or self.freshness_checked_at.utcoffset() is None
        ):
            raise ValueError("Freshness check time must be timezone-aware.")
        if self.freshness_checked_at < self.retrieved_at:
            raise ValueError("Freshness cannot be checked before retrieval.")
        if self.source_data_as_of is not None and (
            not isinstance(self.source_data_as_of, datetime)
            or self.source_data_as_of.utcoffset() is None
        ):
            raise ValueError("Source data time must be timezone-aware.")
        if not isinstance(self.response_complete, bool) or not isinstance(
            self.row_present, bool
        ):
            raise ValueError(
                "Observation completion and row presence must be explicit."
            )
        if not isinstance(self.freshness, MetricFreshness):
            raise ValueError("Observation freshness must be explicit.")
        if self.freshness_rule is not None and not isinstance(
            self.freshness_rule, MetricFreshnessRule
        ):
            raise ValueError("Freshness rule must use the configured rule type.")
        if self.freshness_rule is not None and (
            self.freshness_rule.source != self.source
            or self.freshness_rule.metric_family != self.metric_family
        ):
            raise ValueError(
                "Freshness rule must match the observed source and family."
            )
        expected_freshness = classify_metric_freshness(
            source_data_as_of=self.source_data_as_of,
            checked_at=self.freshness_checked_at,
            rule=self.freshness_rule,
        )
        if self.freshness is not expected_freshness:
            raise ValueError("Freshness must match the configured rule evaluation.")

    def is_complete_for(self, window: ReportingWindow) -> bool:
        """Whether this observation can support a value for the exact window."""

        return (
            self.requested_window == window
            and self.covered_window == window
            and self.response_complete
            and self.row_present
        )


@dataclass(frozen=True)
class CampaignReportMetric:
    """One observed campaign metric or an explicit unavailable state.

    An available numeric zero is valid. Unavailable metrics carry no value, so
    callers cannot accidentally render a missing measurement as zero.
    """

    key: str
    label: str
    status: MetricStatus
    unit: MetricUnit
    window: ReportingWindow | None
    unavailable_reason: MetricUnavailableReason | None = None
    value: int | Decimal | None = None
    currency: str | None = None
    source: str | None = None
    observation: MetricObservation | None = None

    def __post_init__(self):
        if not isinstance(self.status, MetricStatus):
            raise ValueError("Metric status must be explicit.")
        if not isinstance(self.unit, MetricUnit):
            raise ValueError("Metric unit must be explicit.")
        if self.unavailable_reason is not None and not isinstance(
            self.unavailable_reason, MetricUnavailableReason
        ):
            raise ValueError("Unavailable reason must be explicit.")
        if not self.key.strip() or not self.label.strip():
            raise ValueError("Metric key and label are required.")
        if self.window is not None and not isinstance(self.window, ReportingWindow):
            raise ValueError("Reporting window must use the report window type.")
        if self.observation is not None and not isinstance(
            self.observation, MetricObservation
        ):
            raise ValueError("Metric observation must use the observation type.")
        if self.unit is MetricUnit.CURRENCY:
            if (
                not self.currency
                or len(self.currency) != 3
                or not self.currency.isalpha()
            ):
                raise ValueError(
                    "Currency metrics require a three-letter currency code."
                )
            if self.currency != self.currency.upper():
                raise ValueError("Currency code must use uppercase letters.")
        elif self.currency is not None:
            raise ValueError("Count metrics cannot specify a currency.")

        if self.status is MetricStatus.UNAVAILABLE:
            if self.value is not None:
                raise ValueError("Unavailable metrics cannot contain a numeric value.")
            if self.unavailable_reason is None:
                raise ValueError("Unavailable metrics require an explicit reason.")
            if self.unavailable_reason is MetricUnavailableReason.NOT_CONNECTED:
                if self.source is not None or self.observation is not None:
                    raise ValueError(
                        "Not-connected metrics cannot contain source observations."
                    )
            elif self.unavailable_reason is MetricUnavailableReason.UNSUPPORTED:
                if not self.source or not self.source.strip():
                    raise ValueError("Unsupported metrics require the channel source.")
                if self.observation is not None:
                    raise ValueError(
                        "Unsupported metrics cannot claim a source observation."
                    )
            else:
                if not self.source or not self.source.strip():
                    raise ValueError("Partial or stale metrics require a data source.")
                if self.window is None:
                    raise ValueError(
                        "Partial or stale metrics require a reporting window."
                    )
                if self.observation is None:
                    raise ValueError(
                        "Partial or unavailable-freshness metrics require observation evidence."
                    )
                if self.observation.requested_window != self.window:
                    raise ValueError("Observation window must match the metric window.")
                if (
                    self.observation.source != self.source
                    or self.observation.metric_family != self.key
                ):
                    raise ValueError(
                        "Observation source and family must match the metric."
                    )
                is_complete = self.observation.is_complete_for(self.window)
                if self.unavailable_reason is MetricUnavailableReason.PARTIAL:
                    if is_complete:
                        raise ValueError(
                            "Partial metrics cannot claim complete row coverage."
                        )
                else:
                    if not is_complete:
                        raise ValueError(
                            "Stale or unknown-freshness metrics require a complete observed metric row."
                        )
                    expected_freshness = (
                        MetricFreshness.STALE
                        if self.unavailable_reason is MetricUnavailableReason.STALE
                        else MetricFreshness.UNKNOWN
                    )
                    if self.observation.freshness is not expected_freshness:
                        raise ValueError(
                            "Unavailable freshness reason must match its observation."
                        )
            return

        if self.unavailable_reason is not None:
            raise ValueError("Available metrics cannot have an unavailable reason.")
        if self.value is None:
            raise ValueError(
                "Available metrics require a numeric value, including zero."
            )
        if self.window is None:
            raise ValueError("Available metrics require a reporting window.")
        if isinstance(self.value, bool) or not isinstance(self.value, (int, Decimal)):
            raise ValueError("Metric value must be an integer or Decimal.")
        if isinstance(self.value, Decimal) and not self.value.is_finite():
            raise ValueError("Metric value must be finite.")
        if self.value < 0:
            raise ValueError("Metric value must be a non-negative number.")
        if self.unit is MetricUnit.COUNT and not isinstance(self.value, int):
            raise ValueError("Count metrics require an integer value.")
        if not self.source or not self.source.strip():
            raise ValueError("Available metrics require a data source.")
        if self.observation is None or not self.observation.is_complete_for(
            self.window
        ):
            raise ValueError(
                "Available metrics require a complete row for the exact window."
            )
        if (
            self.observation.source != self.source
            or self.observation.metric_family != self.key
        ):
            raise ValueError("Observation source and family must match the metric.")
        if self.observation.freshness is not MetricFreshness.CURRENT:
            raise ValueError(
                "Available metrics require a current source-specific freshness result."
            )

    @property
    def unavailable_message(self) -> str:
        """Short user-facing explanation for an unavailable metric."""

        return {
            MetricUnavailableReason.NOT_CONNECTED: "Veri kaynağı bağlı değil",
            MetricUnavailableReason.UNSUPPORTED: "Bu kanal bu metriği desteklemiyor",
            MetricUnavailableReason.PARTIAL: "Dönem verisi kısmi",
            MetricUnavailableReason.STALE: "Kaynak verisi güncel değil",
            MetricUnavailableReason.FRESHNESS_UNKNOWN: "Kaynak verisinin güncelliği doğrulanamıyor",
        }.get(self.unavailable_reason, "Henüz veri yok")


def unavailable_campaign_report_metrics(
    *, window: ReportingWindow | None, currency: str
) -> tuple[CampaignReportMetric, ...]:
    """Build the current report categories without inventing measurements."""

    categories = (
        ("reach", "Erişim", MetricUnit.COUNT),
        ("impressions", "Gösterimler", MetricUnit.COUNT),
        ("clicks", "Tıklamalar", MetricUnit.COUNT),
        ("interactions", "Diğer etkileşimler", MetricUnit.COUNT),
        ("contact_requests", "İletişim talepleri", MetricUnit.COUNT),
        ("media_spend", "Medya harcaması", MetricUnit.CURRENCY),
    )
    return tuple(
        CampaignReportMetric(
            key=key,
            label=label,
            status=MetricStatus.UNAVAILABLE,
            unit=unit,
            window=window,
            unavailable_reason=MetricUnavailableReason.NOT_CONNECTED,
            currency=currency if unit is MetricUnit.CURRENCY else None,
        )
        for key, label, unit in categories
    )
