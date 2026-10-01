"""Owner-scoped campaign draft application operations."""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from growthtwin.modules.campaigns.models import WorkspaceCampaignDraft
from growthtwin.modules.campaigns.synthetic_rules import (
    ALLOWED_SYNTHETIC_BUDGETS_MINOR,
    ALLOWED_SYNTHETIC_DURATIONS_DAYS,
)
from growthtwin.modules.content.creative import (
    CREATIVE_BODY_MAX_LENGTH,
    CREATIVE_CTA_MAX_LENGTH,
    CREATIVE_HEADLINE_MAX_LENGTH,
    draft_creative_variants,
    source_fingerprint,
)
from growthtwin.modules.content.planning import CampaignBrief
from growthtwin.modules.workspaces.services import get_workspace_for_owner


def get_campaign_draft_for_owner(*, owner, draft_id):
    """Fetch a draft only through the authenticated workspace owner."""

    return WorkspaceCampaignDraft.objects.owned_by(owner).get(pk=draft_id)


def _creative_brief(draft):
    return CampaignBrief(
        text=draft.brief,
        objective=draft.objective,
        objective_label=draft.get_objective_display(),
        target_audience=draft.target_city,
        brand_context=draft.brand_name,
    )


def creative_source_hash_for_draft(draft):
    """Fingerprint the campaign fields used to draft its text variants."""

    return source_fingerprint(_creative_brief(draft))


def generate_creative_version_for_owner(*, owner, draft_id):
    """Append a deterministic creative version only to the owner's draft."""

    with transaction.atomic():
        draft = (
            WorkspaceCampaignDraft.objects.owned_by(owner)
            .select_for_update()
            .get(pk=draft_id)
        )
        brief = _creative_brief(draft)
        source_hash = source_fingerprint(brief)
        versions = list(draft.creative_versions or [])
        if versions and versions[-1].get("source_hash") == source_hash:
            return draft, versions[-1]
        version = {
            "version": len(versions) + 1,
            "source_hash": source_hash,
            "created_at": timezone.now().isoformat(),
            "variants": [
                variant.as_record() for variant in draft_creative_variants(brief)
            ],
        }
        versions.append(version)
        draft.creative_versions = versions
        draft.preferred_creative_key = ""
        draft.preferred_creative_version = None
        draft.save(
            update_fields=(
                "creative_versions",
                "preferred_creative_key",
                "preferred_creative_version",
                "updated_at",
            )
        )
        return draft, version


def select_preferred_creative_for_owner(*, owner, draft_id, version_number, key):
    """Save an informational preference only for a current owner-owned variant."""

    with transaction.atomic():
        draft = (
            WorkspaceCampaignDraft.objects.owned_by(owner)
            .select_for_update()
            .get(pk=draft_id)
        )
        versions = list(draft.creative_versions or [])
        current = versions[-1] if versions else None
        if (
            not current
            or current.get("source_hash") != creative_source_hash_for_draft(draft)
            or current.get("version") != version_number
        ):
            raise ValidationError("Bu reklam metni sürümü artık güncel değil.")
        if not any(
            variant.get("key") == key for variant in current.get("variants", [])
        ):
            raise ValidationError("Bu reklam metni seçeneği bulunamadı.")

        draft.preferred_creative_key = key
        draft.preferred_creative_version = version_number
        draft.save(
            update_fields=(
                "preferred_creative_key",
                "preferred_creative_version",
                "updated_at",
            )
        )
        return draft


def edit_creative_variant_for_owner(
    *, owner, draft_id, version_number, key, headline, body, call_to_action
):
    """Append a validated owner edit to the current synthetic creative history."""

    with transaction.atomic():
        draft = (
            WorkspaceCampaignDraft.objects.owned_by(owner)
            .select_for_update()
            .get(pk=draft_id)
        )
        versions = list(draft.creative_versions or [])
        current = versions[-1] if versions else None
        if (
            not current
            or current.get("source_hash") != creative_source_hash_for_draft(draft)
            or current.get("version") != version_number
        ):
            raise ValidationError("Bu reklam metni sürümü artık güncel değil.")

        edited_fields = {
            "headline": (headline, CREATIVE_HEADLINE_MAX_LENGTH),
            "body": (body, CREATIVE_BODY_MAX_LENGTH),
            "call_to_action": (call_to_action, CREATIVE_CTA_MAX_LENGTH),
        }
        normalized = {}
        for field_name, (value, max_length) in edited_fields.items():
            if not isinstance(value, str):
                raise ValidationError({field_name: "Metin alanı gerekli."})
            value = value.strip()
            if not value:
                raise ValidationError({field_name: "Bu alan boş bırakılamaz."})
            if len(value) > max_length:
                raise ValidationError(
                    {field_name: f"En fazla {max_length} karakter girebilirsin."}
                )
            normalized[field_name] = value

        edited_variants = [dict(variant) for variant in current.get("variants", [])]
        selected_variant = next(
            (variant for variant in edited_variants if variant.get("key") == key),
            None,
        )
        if selected_variant is None:
            raise ValidationError("Düzenlenecek reklam metni bulunamadı.")
        selected_variant.update(normalized)

        version = {
            "version": len(versions) + 1,
            "source_hash": current["source_hash"],
            "created_at": timezone.now().isoformat(),
            "revision_type": "owner_edit",
            "based_on_version": current["version"],
            "edited_variant_key": key,
            "variants": edited_variants,
        }
        versions.append(version)
        draft.creative_versions = versions
        draft.preferred_creative_key = ""
        draft.preferred_creative_version = None
        draft.save(
            update_fields=(
                "creative_versions",
                "preferred_creative_key",
                "preferred_creative_version",
                "updated_at",
            )
        )
        return draft, version


def create_campaign_draft_for_owner(*, owner, workspace_id, **values):
    """Create a draft only in a workspace owned by the supplied user."""

    workspace = get_workspace_for_owner(owner=owner, workspace_id=workspace_id)
    draft = WorkspaceCampaignDraft(workspace=workspace, **values)
    draft.full_clean()
    draft.save()
    return draft


def update_campaign_draft_for_owner(
    *, owner, draft_id, media_budget_minor, flight_start, flight_end
):
    """Update only bounded campaign settings through the owning user."""

    draft = WorkspaceCampaignDraft.objects.owned_by(owner).get(pk=draft_id)
    if media_budget_minor not in ALLOWED_SYNTHETIC_BUDGETS_MINOR:
        raise ValidationError(
            {"media_budget_minor": "Bilinmeyen sentetik bütçe seçeneği."}
        )
    if flight_start is None or flight_end is None:
        raise ValidationError({"flight_end": "Sentetik kampanya süresi gerekli."})
    duration = (flight_end - flight_start).days
    if duration not in ALLOWED_SYNTHETIC_DURATIONS_DAYS:
        raise ValidationError({"flight_end": "Bilinmeyen sentetik süre seçeneği."})

    draft.media_budget_minor = media_budget_minor
    draft.flight_start = flight_start
    draft.flight_end = flight_end
    draft.full_clean()
    draft.save(
        update_fields=("media_budget_minor", "flight_start", "flight_end", "updated_at")
    )
    return draft
