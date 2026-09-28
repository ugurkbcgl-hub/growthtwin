"""Validation for creating a local synthetic campaign draft."""

from django import forms


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
