"""Owned synthetic scene persistence, pinned to one literal identity version.

No asset upload, provider, campaign binding, publication or scene edit history.
"""

from uuid import UUID

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from .creative_scenes import SceneValidationError, seed_scene, validate_scene
from .models import Brand, BrandCreativeDocument


def _owner(owner):
    if not getattr(owner, "is_authenticated", False) or not getattr(
        owner, "is_active", False
    ):
        raise PermissionDenied("Etkin bir marka sahibi hesabı gereklidir.")


def _uuid(value):
    if type(value) is not UUID or not value.int:
        raise ValidationError("Geçerli bir çalışma kimliği gereklidir.")


def _version(value):
    if type(value) is not int or not 1 <= value <= 2**31 - 1:
        raise ValidationError("Geçerli bir çalışma sürümü gereklidir.")


def _brand(owner, brand_id, *, lock=False):
    _owner(owner)
    rows = Brand.objects.select_related("workspace")
    if lock:
        rows = rows.select_for_update()
    return rows.get(
        pk=brand_id,
        workspace__owner=owner,
        workspace__owner__is_active=True,
        is_archived=False,
    )


def _scene(value, fixture):
    try:
        return validate_scene(value, fixture=fixture)
    except SceneValidationError:
        raise ValidationError("Geçerli bir sentetik sahne gereklidir.") from None


def _document(brand, document_id, *, lock=False):
    rows = BrandCreativeDocument.objects.select_related(
        "identity", "identity__brand", "identity__brand__workspace"
    )
    if lock:
        rows = rows.select_for_update()
    return rows.get(pk=document_id, identity__brand=brand)


def create_document(*, owner, brand_id, expected_identity_version, request_id):
    """Create one scene, or replay the same scoped request without overwriting it."""
    _owner(owner)
    _uuid(request_id)
    _version(expected_identity_version)
    with transaction.atomic():
        brand = _brand(owner, brand_id, lock=True)
        existing = (
            BrandCreativeDocument.objects.select_for_update()
            .select_related("identity", "identity__brand", "identity__brand__workspace")
            .filter(pk=request_id)
            .first()
        )
        if existing:
            if (
                existing.identity.brand_id != brand.pk
                or existing.identity.version != expected_identity_version
            ):
                raise ValidationError("Çalışma isteği başka bir bağlamda kullanılmış.")
            _scene(existing.scene, brand.fixture)
            return existing
        if brand.current_version != expected_identity_version:
            raise ValidationError(
                "Marka değişmiş. Güncel marka sürümünden yeni çalışma açın.",
                code="stale_brand_version",
            )
        identity = brand.current_identity
        try:
            scene = seed_scene(
                fixture=brand.fixture,
                tagline_text=identity.tagline_text,
                primary_color=identity.primary_color,
                logo_key=identity.logo_key,
            )
        except SceneValidationError:
            raise ValidationError(
                "Geçerli bir sentetik marka kimliği gereklidir."
            ) from None
        try:
            with transaction.atomic():
                document = BrandCreativeDocument.objects.create(
                    id=request_id, identity=identity, scene=scene
                )
        except IntegrityError:
            raise ValidationError(
                "Çalışma isteği başka bir bağlamda kullanılmış."
            ) from None
        return document


def read_document(*, owner, brand_id, document_id):
    _uuid(document_id)
    brand = _brand(owner, brand_id)
    document = _document(brand, document_id)
    _scene(document.scene, brand.fixture)
    return document


def save_document(*, owner, brand_id, document_id, expected_revision, scene):
    """Compare-and-save current scene; retain the original identity forever."""
    _owner(owner)
    _uuid(document_id)
    _version(expected_revision)
    with transaction.atomic():
        brand = _brand(owner, brand_id, lock=True)
        document = _document(brand, document_id, lock=True)
        if document.revision != expected_revision:
            raise ValidationError(
                "Çalışma değişmiş. Güncel sürümü açıp yeniden deneyin.",
                code="stale_document_revision",
            )
        canonical = _scene(scene, brand.fixture)
        if document.scene == canonical:
            return document
        if document.revision == 2**31 - 1:
            raise ValidationError("Çalışma sürümü sınırına ulaşıldı.")
        changed = BrandCreativeDocument.objects.filter(
            pk=document.pk,
            identity_id=document.identity_id,
            revision=expected_revision,
        ).update(
            scene=canonical, revision=expected_revision + 1, updated_at=timezone.now()
        )
        if changed != 1:
            raise ValidationError(
                "Çalışma değişmiş. Güncel sürümü açıp yeniden deneyin.",
                code="stale_document_revision",
            )
        document.refresh_from_db()
        return document
