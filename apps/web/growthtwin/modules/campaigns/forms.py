"""Authenticated launch form for a fixed synthetic campaign example."""

from django import forms

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
