from django import forms
from .models import Character, Faction, Location, Race


class CreateCharacterForm(forms.ModelForm):
    name = forms.CharField(max_length=50, required=True)
    faction = forms.ModelChoiceField(
        label="Facción", queryset=Faction.objects.all(), required=True
    )
    location = forms.ModelChoiceField(
        label="Ubicacion", queryset=Location.objects.all(), required=True
    )
    race = forms.ModelChoiceField(
        label="Raza", queryset=Race.objects.all(), required=True
    )

    class Meta:
        model = Character
        fields = ["name", "faction", "location", "race"]
