"""Immutable local review packages, with no dispatch or approval authority."""

import hashlib
import json
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from growthtwin.modules.campaigns.exports import preferred_current_variant
from growthtwin.modules.campaigns.planning import (
    _fit_text,
    build_google_search_campaign_plan,
)

MAPPER_VERSION = "google-search-review-v1"


@dataclass(frozen=True)
class GoogleDraftPackage:
    """Canonical JSON is immutable; callers deserialize their own review copy."""

    payload_json: str
    fingerprint: str


def _assets(candidates, *, limit, count, kind):
    assets, changes, seen = [], [], set()
    for original, source in candidates:
        mapped = _fit_text(original, max_characters=limit)
        if not mapped or mapped.casefold() in seen:
            continue
        seen.add(mapped.casefold())
        assets.append(mapped)
        changes.append(
            {
                "asset": kind,
                "index": len(assets) - 1,
                "source": source,
                "original": original,
                "mapped": mapped,
                "shortened": len(" ".join(original.split())) > limit,
                "normalized": original != " ".join(original.split()),
                "max_characters": limit,
            }
        )
        if len(assets) == count:
            break
    if len(assets) != count:
        raise ValidationError(
            "Yeterli sayıda farklı Google reklam metni hazırlanamadı."
        )
    return assets, changes


def build_draft_package(draft):
    """Map only a current preference; freeze every input that affects review."""

    selected = preferred_current_variant(draft)
    if selected is None:
        raise ValidationError("Güncel reklam metnini yeniden seçmelisin.")
    plan = build_google_search_campaign_plan(draft)
    if (
        not plan.ready_for_review
        or draft.channel != "google_search"
        or plan.currency != "TRY"
        or plan.flight_end < plan.flight_start
    ):
        raise ValidationError(
            "Google Search için kanal, para birimi ve planı tamamlamalısın."
        )
    URLValidator(schemes=["http", "https"])(plan.final_url)
    if any(
        not isinstance(selected.get(field), str) or not selected[field].strip()
        for field in ("headline", "body", "call_to_action")
    ):
        raise ValidationError("Seçili reklam metni eksik.")

    # Recover fallback originals so pre-shortening in the plan is never hidden.
    brand = " ".join(draft.brand_name.split())
    city = " ".join(draft.target_city.split())
    headline_originals = {
        ("brand_name",): draft.brand_name,
        ("target_city", "brand_name"): f"{city} {brand}",
    }
    fallback_headlines = [
        (
            f"{brand} hakkında"
            if asset.text == _fit_text(f"{brand} hakkında", max_characters=30)
            else headline_originals.get(asset.source_fields, asset.text),
            "plan." + "+".join(asset.source_fields),
        )
        for asset in plan.headlines
    ]
    fallback_descriptions = [
        (
            draft.brief
            if asset.source_fields == ("brief",)
            else f"İşletmeyi ve hizmetlerini web sitesinde inceleyin: {brand}.",
            "plan." + "+".join(asset.source_fields),
        )
        for asset in plan.descriptions
    ]
    headlines, headline_changes = _assets(
        [
            (selected["headline"], "selected.headline"),
            (selected["call_to_action"], "selected.call_to_action"),
            *fallback_headlines,
        ],
        limit=30,
        count=3,
        kind="headline",
    )
    descriptions, description_changes = _assets(
        [
            (selected["body"], "selected.body"),
            (selected["call_to_action"], "selected.call_to_action"),
            *fallback_descriptions,
        ],
        limit=90,
        count=2,
        kind="description",
    )
    payload = {
        "mapper_version": MAPPER_VERSION,
        "source": {
            "draft_id": draft.pk,
            "workspace_id": draft.workspace_id,
            "version": draft.preferred_creative_version,
            "key": draft.preferred_creative_key,
            "selected": selected,
            "creative_source_hash": draft.creative_versions[-1]["source_hash"],
            "name": draft.name,
            "brand_name": draft.brand_name,
            "brief": draft.brief,
            "objective": draft.objective,
            "channel": draft.channel,
            "target_city": draft.target_city,
        },
        "google": {
            "headlines": headlines,
            "descriptions": descriptions,
            "final_url": plan.final_url,
            "currency": plan.currency,
            "media_budget_minor": plan.media_budget_minor,
            "start": plan.flight_start.isoformat(),
            "end": plan.flight_end.isoformat(),
            "target_city": plan.target_city,
            "status": "PAUSED",
        },
        "transformations": headline_changes + description_changes,
        "validation": {
            "status": "local_review_only",
            "google_approval": False,
            "destination_reachability_verified": False,
            "publication_enabled": False,
        },
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return GoogleDraftPackage(
        encoded, hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    )
