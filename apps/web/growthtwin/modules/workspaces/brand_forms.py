"""Bounded synthetic brand forms; no advertiser data is collected."""

from django import forms

from growthtwin.modules.workspaces.models import Workspace
from growthtwin.modules.workspaces.services import SYNTHETIC_BRAND_PRESETS

PALETTE = (
    ("#245C48", "Orman yeşili"),
    ("#F4E8D2", "Sıcak krem"),
    ("#254D9B", "Güven mavisi"),
    ("#EAF0FF", "Buz mavisi"),
    ("#9A3F2D", "Kiremit"),
    ("#F6CD65", "Güneş sarısı"),
)
TONES = (
    ("calm", "Sakin ve samimi"),
    ("energetic", "Enerjik ve canlı"),
    ("formal", "Resmî ve güven veren"),
)


class BrandCreateForm(forms.Form):
    workspace = forms.ModelChoiceField(
        label="Çalışma alanı", queryset=Workspace.objects.none()
    )
    fixture = forms.ChoiceField(
        label="Örnek marka",
        choices=(("product", "Ürün markası"), ("service", "Hizmet markası")),
    )

    def __init__(self, *args, owner, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["workspace"].queryset = Workspace.objects.filter(owner=owner)


class BrandIdentityForm(forms.Form):
    expected_version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    primary_color = forms.ChoiceField(label="Ana renk", choices=PALETTE)
    secondary_color = forms.ChoiceField(label="Tamamlayıcı renk", choices=PALETTE)
    tone = forms.ChoiceField(label="Markanın konuşma biçimi", choices=TONES)
    tagline_key = forms.ChoiceField(label="Marka mesajı")

    def __init__(self, *args, brand, **kwargs):
        super().__init__(*args, **kwargs)
        preset = SYNTHETIC_BRAND_PRESETS[brand.fixture]
        self.fields["tagline_key"].choices = tuple(preset["taglines"].items())
        current = brand.current_identity
        if current:
            for name in ("primary_color", "secondary_color"):
                value = getattr(current, name)
                if value not in dict(PALETTE):
                    self.fields[name].choices = (
                        *PALETTE,
                        (value, "Mevcut marka rengi"),
                    )
