from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Character


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CreateCharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ["icon", "name", "sex", "faction", "location", "race"]
        widgets = {"icon": forms.HiddenInput}

