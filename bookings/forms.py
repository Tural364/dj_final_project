from django import forms
from .models import BookingRequest

class BookingRequestForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = ("message",)
        widgets = {"message": forms.Textarea(attrs={"rows": 3, "placeholder": "Расскажите, чему хотите научиться..."})}
