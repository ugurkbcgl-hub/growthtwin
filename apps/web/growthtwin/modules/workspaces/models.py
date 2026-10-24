"""Synthetic workspace records owned by authenticated users."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

SYNTHETIC_BRAND_PRESETS = {
    "product": {
        "name": "Duru · Örnek seramik atölyesi",
        "facts": (
            "Kurgusal seramik ürün örneği.",
            "Gerçek ürün, fiyat, stok veya satış vaadi içermez.",
        ),
        "logo_key": "product:logo:v1",
        "primary_color": "#244c3b",
        "secondary_color": "#f5eddf",
        "default_tagline": "small_beauty",
        "taglines": {
            "small_beauty": "Gününe küçük bir güzellik.",
            "daily_detail": "Günlük hayatına özenli bir detay.",
        },
    },
    "service": {
        "name": "Özen · Örnek ev bakımı",
        "facts": (
            "Ankara için kurgusal ev bakım hizmeti örneği.",
            "Gerçek işletme, müşteri talebi veya hizmet garantisi içermez.",
        ),
        "logo_key": "service:logo:v1",
        "primary_color": "#244c3b",
        "secondary_color": "#e9efe2",
        "default_tagline": "careful_touch",
        "taglines": {
            "careful_touch": "Evin için özenli bir dokunuş.",
            "city_care": "Şehrinde özenli bakım.",
        },
    },
}

HEX_COLOR_VALIDATOR = RegexValidator(
    regex=r"\A#[0-9a-fA-F]{6}\Z", message="Altı basamaklı bir renk seçin."
)


class Workspace(models.Model):
    """Owner-scoped tenant boundary for authenticated brands and campaign drafts."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workspaces",
    )
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name", "pk")

    def __str__(self) -> str:
        return self.name


class Brand(models.Model):
    """One of two fixed synthetic brands in an explicitly owned workspace."""

    class Fixture(models.TextChoices):
        PRODUCT = "product", "Ürün · Seramik örneği"
        SERVICE = "service", "Hizmet · Ev bakımı örneği"

    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="brands"
    )
    name = models.CharField(max_length=120)
    fixture = models.CharField(max_length=16, choices=Fixture.choices)
    is_archived = models.BooleanField(default=False)
    current_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name", "pk")
        constraints = [
            models.UniqueConstraint(
                fields=("workspace", "fixture"), name="brand_workspace_fixture_unique"
            ),
            models.CheckConstraint(
                condition=models.Q(current_version__gte=1),
                name="brand_current_version_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(fixture__in=("product", "service")),
                name="brand_fixed_synthetic_fixture",
            ),
        ]

    @property
    def current_identity(self):
        return self.identities.get(version=self.current_version)

    @property
    def synthetic_facts(self):
        return SYNTHETIC_BRAND_PRESETS[self.fixture]["facts"]

    def __str__(self):
        return self.name


class BrandIdentityQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError("Marka sürümleri değiştirilemez; yeni sürüm oluşturun.")

    def delete(self):
        raise ValidationError("Marka sürümleri tek başına silinemez.")


class BrandIdentity(models.Model):
    """Append-only identity snapshots via the application API, not a SQL vault."""

    class Tone(models.TextChoices):
        CALM = "calm", "Sakin"
        ENERGETIC = "energetic", "Enerjik"
        FORMAL = "formal", "Resmî"

    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="identities"
    )
    version = models.PositiveIntegerField()
    primary_color = models.CharField(max_length=7, validators=[HEX_COLOR_VALIDATOR])
    secondary_color = models.CharField(max_length=7, validators=[HEX_COLOR_VALIDATOR])
    tone = models.CharField(max_length=16, choices=Tone.choices)
    tagline_key = models.CharField(max_length=32)
    tagline_text = models.CharField(max_length=100)
    logo_key = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BrandIdentityQuerySet.as_manager()

    class Meta:
        ordering = ("-version",)
        constraints = [
            models.UniqueConstraint(
                fields=("brand", "version"), name="brand_identity_version_unique"
            ),
            models.CheckConstraint(
                condition=models.Q(version__gte=1),
                name="brand_identity_version_positive",
            ),
        ]

    @property
    def tagline(self):
        return self.tagline_text

    def clean(self):
        super().clean()
        if not self.brand_id:
            return
        preset = SYNTHETIC_BRAND_PRESETS.get(self.brand.fixture)
        if not preset or self.tagline_key not in preset["taglines"]:
            raise ValidationError({"tagline_key": "Bu örneğe ait bir metin seçin."})
        if self.tagline_text != preset["taglines"][self.tagline_key]:
            raise ValidationError(
                {"tagline_text": "Metin seçilen sabit örnekle eşleşmeli."}
            )
        if self.logo_key != preset["logo_key"]:
            raise ValidationError(
                {"logo_key": "Yalnız sabit örnek logo kullanılabilir."}
            )

    def save(self, *args, **kwargs):
        if not self._state.adding or self.pk is not None:
            raise ValidationError(
                "Marka sürümleri değiştirilemez; yeni sürüm oluşturun."
            )
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Marka sürümleri tek başına silinemez.")
