"""Provider-free text starting points for the local campaign prototype."""

from dataclasses import asdict, dataclass
from hashlib import sha256
from textwrap import shorten

from growthtwin.modules.content.planning import CampaignBrief


@dataclass(frozen=True)
class CreativeVariant:
    """An editable ad-copy starting point with no generated factual claims."""

    key: str
    angle: str
    headline: str
    body: str
    call_to_action: str

    def as_record(self) -> dict[str, str]:
        """Return a JSONField-compatible representation."""
        return asdict(self)


def source_fingerprint(brief: CampaignBrief) -> str:
    """Identify the brief context used to create the current copy suggestions."""
    source = "\x1f".join(
        (
            brief.text.strip(),
            brief.brand_context.strip(),
            brief.target_audience.strip(),
        )
    )
    return sha256(source.encode("utf-8")).hexdigest()


def draft_creative_variants(brief: CampaignBrief) -> tuple[CreativeVariant, ...]:
    """Format advertiser-provided text into conservative, editable examples."""
    brand_context = " ".join(brief.brand_context.split())
    subject = brand_context or " ".join(brief.text.split())
    brief_text = " ".join(brief.text.split())
    audience = " ".join(brief.target_audience.split())
    headline = shorten(subject, width=80, placeholder="…")
    short_brief = shorten(brief_text, width=240, placeholder="…")
    audience_copy = (
        f"{audience} için: {shorten(subject, width=190, placeholder='…')}"
        if audience
        else f"{short_brief} Detayları incele."
    )
    info_copy = (
        f"{shorten(brand_context, width=190, placeholder='…')} hakkında detayları incele."
        if brand_context
        else short_brief
    )

    return (
        CreativeVariant(
            key="short-introduction",
            angle="Kısa tanıtım",
            headline=headline,
            body=short_brief,
            call_to_action="Detayları incele",
        ),
        CreativeVariant(
            key="audience-focused",
            angle="Kitle odağı",
            headline=headline,
            body=shorten(audience_copy, width=240, placeholder="…"),
            call_to_action="Daha fazlasını keşfet",
        ),
        CreativeVariant(
            key="information-focused",
            angle="Bilgi odağı",
            headline=(
                shorten(f"{brand_context} hakkında", width=80, placeholder="…")
                if brand_context
                else "Daha fazla bilgi"
            ),
            body=shorten(info_copy, width=240, placeholder="…"),
            call_to_action="Bilgi al",
        ),
    )
