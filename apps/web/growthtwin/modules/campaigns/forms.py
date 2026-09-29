"""Authenticated launch form for a fixed synthetic campaign example."""

from django import forms

from growthtwin.modules.campaigns.synthetic_rules import (
    SYNTHETIC_BUDGET_CHOICES,
    SYNTHETIC_DURATION_CHOICES,
)
from growthtwin.modules.workspaces.models import Workspace


class CampaignDraftForm(forms.Form):
    workspace = forms.ModelChoiceField(
        queryset=Workspace.objects.none(),
        label="Çalışma alanı",
    )
    synthetic_confirmation = forms.BooleanField(
        required=True,
        label="Bu prototipte yalnız sentetik örnek bilgi kullanıyorum.",
    )

    def __init__(self, *args, workspaces, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["workspace"].queryset = workspaces


class CampaignDraftEditForm(forms.Form):
    """Allow changes to bounded demo settings, never advertiser-supplied text."""

    media_budget_minor = forms.ChoiceField(
        choices=SYNTHETIC_BUDGET_CHOICES,
        label="Örnek medya bütçesi",
    )
    duration_days = forms.ChoiceField(
        choices=SYNTHETIC_DURATION_CHOICES,
        label="Örnek kampanya süresi",
    )
    synthetic_confirmation = forms.BooleanField(
        required=True,
        initial=True,
        label="Yalnız sentetik örnek ayarlarını değiştiriyorum.",
    )
