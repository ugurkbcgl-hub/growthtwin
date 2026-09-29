"""Provider-neutral values for campaign report metrics."""

from dataclasses import dataclass
from datetime import date, datetime
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


class MetricUnit(StrEnum):
    """Supported measurement kinds for the first reporting contract."""

    COUNT = "count"
    CURRENCY = "currency"


@dataclass(frozen=True)
class ReportingWindow:
    """Inclusive dates covered by a report metric."""

    start: date
    end: date

    def __post_init__(self):
        if self.start > self.end:
            raise ValueError("Reporting window end must not precede its start.")


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
    observed_at: datetime | None = None

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
                if self.source is not None or self.observed_at is not None:
                    raise ValueError(
                        "Not-connected metrics cannot contain source observations."
                    )
            elif self.unavailable_reason is MetricUnavailableReason.UNSUPPORTED:
                if not self.source or not self.source.strip():
                    raise ValueError("Unsupported metrics require the channel source.")
                if self.observed_at is not None:
                    raise ValueError(
                        "Unsupported metrics cannot claim an observation time."
                    )
            else:
                if not self.source or not self.source.strip():
                    raise ValueError("Partial or stale metrics require a data source.")
                if self.window is None:
                    raise ValueError(
                        "Partial or stale metrics require a reporting window."
                    )
                if (
                    not isinstance(self.observed_at, datetime)
                    or self.observed_at.utcoffset() is None
                ):
                    raise ValueError(
                        "Partial or stale metrics require an aware observation time."
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
        if (
            not isinstance(self.observed_at, datetime)
            or self.observed_at.utcoffset() is None
        ):
            raise ValueError(
                "Available metrics require a timezone-aware observation time."
            )

    @property
    def unavailable_message(self) -> str:
        """Short user-facing explanation for an unavailable metric."""

        return {
            MetricUnavailableReason.NOT_CONNECTED: "Veri kaynağı bağlı değil",
            MetricUnavailableReason.UNSUPPORTED: "Bu kanal bu metriği desteklemiyor",
            MetricUnavailableReason.PARTIAL: "Dönem verisi kısmi",
            MetricUnavailableReason.STALE: "Kaynak verisi güncel değil",
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
