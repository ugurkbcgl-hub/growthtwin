"""Forms for the synthetic Phase 0 profile screen."""

from django import forms

from growthtwin.demo.models import DemoProfile


class DemoProfileForm(forms.ModelForm):
    class Meta:
        model = DemoProfile
        fields = ("clinic_name", "city", "phone", "website")
        labels = {
            "clinic_name": "Klinik adı",
            "city": "Şehir",
            "phone": "Telefon",
            "website": "Web sitesi",
        }
        widgets = {
            "clinic_name": forms.TextInput(attrs={"autocomplete": "organization"}),
            "city": forms.TextInput(attrs={"autocomplete": "address-level2"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel"}),
            "website": forms.URLInput(attrs={"autocomplete": "url"}),
        }
