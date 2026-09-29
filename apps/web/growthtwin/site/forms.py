"""Validation for creating a local synthetic campaign draft."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from growthtwin.modules.content.creative import CreativeVariant
from growthtwin.site.models import CampaignObjective


class CampaignDraftForm(forms.Form):
    campaign_id = forms.UUIDField(required=False, widget=forms.HiddenInput())
    brief = forms.CharField(
        label="Kampanya fikrin",
        max_length=280,
        strip=True,
        widget=forms.Textarea(
            attrs={
                "id": "campaign-brief",
                "maxlength": "280",
                "placeholder": (
                    "Örn. Yeni açılan atölyem için daha fazla yerel müşteri bulmak istiyorum."
                ),
                "rows": "3",
            }
        ),
        error_messages={"required": "Kısaca kampanya fikrini yaz."},
    )
    brand_context = forms.CharField(
        label="Marka ve ürün hakkında",
        required=False,
        max_length=320,
        strip=True,
        widget=forms.Textarea(
            attrs={
                "id": "brand-context",
                "maxlength": "320",
                "placeholder": "Örn. Mahalle fırını; günlük ekşi mayalı ekmek ve kahvaltı kutuları sunuyor.",
                "rows": "2",
            }
        ),
    )
    target_audience = forms.CharField(
        label="Hedef kitlen",
        required=False,
        max_length=240,
        strip=True,
        widget=forms.Textarea(
            attrs={
                "id": "target-audience",
                "maxlength": "240",
                "placeholder": "Örn. Hafta içi öğle yemeği arayan, yakındaki çalışanlar.",
                "rows": "2",
            }
        ),
    )
    objective = forms.ChoiceField(
        label="Kampanyadan ne bekliyorsun?",
        required=False,
        choices=(("", "Şimdilik seçmek istemiyorum"), *CampaignObjective.choices),
        widget=forms.Select(attrs={"id": "campaign-objective"}),
    )
    daily_limit = forms.IntegerField(
        label="Günlük üst sınır",
        min_value=100,
        max_value=100000,
        initial=750,
        widget=forms.NumberInput(
            attrs={
                "id": "daily-limit",
                "inputmode": "numeric",
                "step": "50",
            }
        ),
    )
    duration_days = forms.TypedChoiceField(
        label="Süre",
        choices=((7, "7 gün"), (14, "14 gün"), (30, "30 gün")),
        coerce=int,
        initial=7,
        widget=forms.Select(attrs={"id": "campaign-days"}),
    )


class CreativeVariantsForm(forms.Form):
    """Validate editable text fields while preserving variant metadata."""

    def __init__(self, *args, variants, **kwargs):
        super().__init__(*args, **kwargs)
        self.variants = [
            variant.as_record() if isinstance(variant, CreativeVariant) else variant
            for variant in variants
        ]
        for index, variant in enumerate(self.variants):
            self.fields[f"headline_{index}"] = forms.CharField(
                label="Başlık",
                max_length=80,
                widget=forms.TextInput(attrs={"maxlength": "80"}),
                initial=variant["headline"],
            )
            self.fields[f"body_{index}"] = forms.CharField(
                label="Reklam metni",
                max_length=240,
                widget=forms.Textarea(attrs={"maxlength": "240", "rows": "3"}),
                initial=variant["body"],
            )
            self.fields[f"call_to_action_{index}"] = forms.CharField(
                label="Eylem metni",
                max_length=48,
                widget=forms.TextInput(attrs={"maxlength": "48"}),
                initial=variant["call_to_action"],
            )

    def cleaned_variants(self):
        """Return validated copy fields alongside their stable angle labels."""
        if not self.is_valid():
            raise ValueError("Creative variant fields must be valid before saving.")

        return [
            {
                **{key: variant[key] for key in ("key", "angle") if key in variant},
                "headline": self.cleaned_data[f"headline_{index}"],
                "body": self.cleaned_data[f"body_{index}"],
                "call_to_action": self.cleaned_data[f"call_to_action_{index}"],
            }
            for index, variant in enumerate(self.variants)
        ]


class GrowthTwinAuthenticationForm(AuthenticationForm):
    """Use Turkish labels and password-manager hints on the login screen."""

    username = forms.CharField(
        label="Kullanıcı adı",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "username",
                "autocapitalize": "none",
                "spellcheck": "false",
            }
        ),
    )
    password = forms.CharField(
        label="Parola",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
