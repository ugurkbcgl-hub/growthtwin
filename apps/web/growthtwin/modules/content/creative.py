"""Provider-free text starting points for the local campaign prototype."""

from dataclasses import asdict, dataclass
from hashlib import sha256

from growthtwin.modules.content.planning import CampaignBrief

CREATIVE_HEADLINE_MAX_LENGTH = 80
CREATIVE_BODY_MAX_LENGTH = 240
CREATIVE_CTA_MAX_LENGTH = 40


def _shorten_preserving_ends(value: str, *, width: int) -> str:
    """Fit copy to a field while retaining context from its beginning and end."""
    words = value.split()
    if len(" ".join(words)) <= width:
        return " ".join(words)

    marker = "…"
    content_width = width - len(marker)
    head_budget = content_width // 3
    tail_budget = content_width - head_budget

    head: list[str] = []
    used = 0
    for word in words:
        needed = len(word) + bool(head)
        if used + needed > head_budget:
            break
        head.append(word)
        used += needed

    tail: list[str] = []
    used = 0
    for word in reversed(words[len(head) :]):
        needed = len(word) + bool(tail)
        if used + needed > tail_budget:
            break
        tail.append(word)
        used += needed

    if not head and not tail:
        return f"{value[:head_budget]}{marker}{value[-tail_budget:]}"
    if not head:
        return f"{marker}{' '.join(reversed(tail))}"
    if not tail:
        return f"{' '.join(head)}{marker}{words[len(head)][:tail_budget]}"

    return f"{' '.join(head)}{marker}{' '.join(reversed(tail))}"


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
    headline = _shorten_preserving_ends(subject, width=CREATIVE_HEADLINE_MAX_LENGTH)
    short_brief = _shorten_preserving_ends(brief_text, width=CREATIVE_BODY_MAX_LENGTH)
    audience_copy = (
        f"{_shorten_preserving_ends(audience, width=70)} için: "
        f"{_shorten_preserving_ends(brief_text, width=160)}"
        if audience
        else short_brief
    )
    info_copy = short_brief

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
            body=_shorten_preserving_ends(
                audience_copy, width=CREATIVE_BODY_MAX_LENGTH
            ),
            call_to_action="Daha fazlasını keşfet",
        ),
        CreativeVariant(
            key="information-focused",
            angle="Bilgi odağı",
            headline=(
                _shorten_preserving_ends(
                    f"{brand_context} hakkında", width=CREATIVE_HEADLINE_MAX_LENGTH
                )
                if brand_context
                else "Daha fazla bilgi"
            ),
            body=_shorten_preserving_ends(info_copy, width=CREATIVE_BODY_MAX_LENGTH),
            call_to_action="Bilgi al",
        ),
    )
