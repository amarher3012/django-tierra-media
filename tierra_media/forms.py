from django import forms
from .models import Character


class CreateCharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ["name", "faction", "location", "race", "user"]
