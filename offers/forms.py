from django import forms
from .models import SkillOffer

class SkillOfferForm(forms.ModelForm):
    class Meta:
        model = SkillOffer
        fields = ("title", "description", "category", "image", "level", "format", "duration_minutes")
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}

    def clean_duration_minutes(self):
        value = self.cleaned_data["duration_minutes"]
        if value < 15 or value > 480:
            raise forms.ValidationError("Длительность должна быть от 15 до 480 минут.")
        return value
