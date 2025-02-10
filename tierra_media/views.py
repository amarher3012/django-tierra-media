from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import CustomUserCreationForm

# Create your views here.

class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('tierra_media:login')

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f'Cuenta {user.username} creada exitosamente. Ahora puedes iniciar sesión.')
        return super().form_valid(form)

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "tierra_media/index.html"