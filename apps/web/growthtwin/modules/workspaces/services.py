"""Owner-scoped workspace application queries."""

import re

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from growthtwin.modules.workspaces.models import (
    SYNTHETIC_BRAND_PRESETS,
    Brand,
    BrandIdentity,
    Workspace,
)


def get_workspace_for_owner(*, owner, workspace_id):
    """Fetch a workspace only when the authenticated user owns it."""

    if not getattr(owner, "is_authenticated", False):
        raise PermissionDenied("An authenticated workspace owner is required.")
    return Workspace.objects.get(pk=workspace_id, owner=owner)


def get_brand_for_owner(*, owner, brand_id):
    if not getattr(owner, "is_authenticated", False):
        raise PermissionDenied("An authenticated workspace owner is required.")
    return Brand.objects.select_related("workspace").get(
        pk=brand_id, workspace__owner=owner, is_archived=False
    )


def list_brands_for_owner(*, owner, workspace_id):
    workspace = get_workspace_for_owner(owner=owner, workspace_id=workspace_id)
    return Brand.objects.filter(workspace=workspace, is_archived=False)


def create_brand_for_owner(*, owner, workspace_id, fixture):
    """Create a fixed example once; repeated submissions reuse its saved versions."""
    workspace = get_workspace_for_owner(owner=owner, workspace_id=workspace_id)
    if not isinstance(fixture, str) or fixture not in SYNTHETIC_BRAND_PRESETS:
        raise ValidationError("Geçerli bir sentetik marka örneği seçin.")
    preset = SYNTHETIC_BRAND_PRESETS[fixture]
    with transaction.atomic():
        Workspace.objects.select_for_update().get(pk=workspace.pk, owner=owner)
        brand, created = Brand.objects.get_or_create(
            workspace=workspace,
            fixture=fixture,
            defaults={"name": preset["name"]},
        )
        if brand.is_archived:
            raise ValidationError(
                "Bu örnek arşivlenmiş; otomatik olarak yeniden açılmaz."
            )
        if created:
            BrandIdentity.objects.create(
                brand=brand,
                version=1,
                primary_color=preset["primary_color"],
                secondary_color=preset["secondary_color"],
                tone=BrandIdentity.Tone.CALM,
                tagline_key=preset["default_tagline"],
                tagline_text=preset["taglines"][preset["default_tagline"]],
                logo_key=preset["logo_key"],
            )
        return brand


def update_brand_identity_for_owner(
    *,
    owner,
    brand_id,
    expected_version,
    primary_color,
    secondary_color,
    tone,
    tagline_key,
):
    """Append one immutable snapshot under an owner-scoped optimistic revision."""
    scoped = get_brand_for_owner(owner=owner, brand_id=brand_id)
    if type(expected_version) is not int or expected_version < 1:
        raise ValidationError("Geçerli bir marka sürümü gereklidir.")
    for color in (primary_color, secondary_color):
        if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            raise ValidationError("Altı basamaklı bir renk seçin.")
    if not isinstance(tone, str) or tone not in BrandIdentity.Tone.values:
        raise ValidationError("Geçerli bir anlatım tonu seçin.")
    preset = SYNTHETIC_BRAND_PRESETS[scoped.fixture]
    if not isinstance(tagline_key, str) or tagline_key not in preset["taglines"]:
        raise ValidationError("Bu örneğe ait bir metin seçin.")
    with transaction.atomic():
        brand = Brand.objects.select_for_update().get(
            pk=scoped.pk, workspace__owner=owner, is_archived=False
        )
        if brand.current_version != expected_version:
            raise ValidationError(
                "Marka değişmiş. Güncel sürümü açıp yeniden deneyin.",
                code="stale_brand_version",
            )
        current = brand.current_identity
        values = {
            "primary_color": primary_color.lower(),
            "secondary_color": secondary_color.lower(),
            "tone": tone,
            "tagline_key": tagline_key,
        }
        if all(getattr(current, field) == value for field, value in values.items()):
            return current
        next_version = current.version + 1
        changed = Brand.objects.filter(
            pk=brand.pk, workspace__owner=owner, current_version=expected_version
        ).update(current_version=next_version)
        if changed != 1:
            raise ValidationError(
                "Marka değişmiş. Güncel sürümü açıp yeniden deneyin.",
                code="stale_brand_version",
            )
        return BrandIdentity.objects.create(
            brand=brand,
            version=next_version,
            logo_key=preset["logo_key"],
            tagline_text=preset["taglines"][tagline_key],
            **values,
        )
