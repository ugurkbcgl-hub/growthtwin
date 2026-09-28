"""Provider-neutral campaign-plan values derived from advertiser inputs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MissingPlanInput:
    """An optional input that could make a local plan clearer."""

    field_id: str
    label: str
    guidance: str


@dataclass(frozen=True)
class CampaignBrief:
    """Advertiser intent and context, independent of storage or HTTP."""

    text: str
    objective: str
    objective_label: str
    target_audience: str
    brand_context: str

    @property
    def objective_summary(self) -> str:
        return self.objective_label or "Brief’ten netleştirilecek"

    @property
    def audience_summary(self) -> str:
        return self.target_audience or "Henüz belirtilmedi"

    @property
    def brand_summary(self) -> str:
        return self.brand_context or "Henüz belirtilmedi"

    @property
    def missing_inputs(self) -> tuple[MissingPlanInput, ...]:
        missing = []
        if not self.objective:
            missing.append(
                MissingPlanInput(
                    field_id="campaign-objective",
                    label="Kampanya amacı",
                    guidance=(
                        "Başarı senin için ne demek? Örneğin ziyaret, potansiyel "
                        "müşteri veya satış."
                    ),
                )
            )
        if not self.target_audience:
            missing.append(
                MissingPlanInput(
                    field_id="target-audience",
                    label="Hedef kitle",
                    guidance="Ulaşmak istediğin kişileri kısaca tarif edebilirsin.",
                )
            )
        if not self.brand_context:
            missing.append(
                MissingPlanInput(
                    field_id="brand-context",
                    label="Marka veya teklif",
                    guidance="Tanıtılan ürün, hizmet veya teklifi ekleyebilirsin.",
                )
            )
        return tuple(missing)

    @property
    def first_missing_field(self) -> str:
        return self.missing_inputs[0].field_id if self.missing_inputs else ""


@dataclass(frozen=True)
class CampaignPlan:
    """An immutable, non-persistent plan derived from a brief and limits."""

    brief: CampaignBrief
    daily_limit: int
    duration_days: int

    @property
    def total_limit(self) -> int:
        return self.daily_limit * self.duration_days
