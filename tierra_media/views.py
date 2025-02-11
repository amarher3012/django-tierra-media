from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlencode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import FormView, TemplateView
from .forms import CustomUserCreationForm
import copy
from django.views.generic import *
from .forms import CreateCharacterForm
from .models import Character
from .constants import NPCS


class RegisterView(FormView):
    template_name = "registration/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("tierra_media:index")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        token = default_token_generator.make_token(user)

        uid = user.pk
        token_url = self.build_activation_url(uid, token)

        self.send_activation_email(user, token_url)

        messages.success(
            self.request,
            f"Cuenta {user.username} creada exitosamente. En breves te llegará un correo de verificación.",
        )

        return super().form_valid(form)

    def build_activation_url(self, uid, token):
        return f"{get_current_site(self.request).domain}{reverse_lazy('tierra_media:activate')}?{urlencode({'uid': uid, 'token': token})}"

    def send_activation_email(self, user, token_url):
        subject = "Verificación de correo electrónico"
        message = (
            f"Hola {user.username},\n\nPara activar tu cuenta, haz clic en el siguiente enlace:\n\n{token_url}\n\n"
            f"Si no solicitaste esta cuenta, puedes ignorar este correo."
        )
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)


class ActivateAccount(View):
    def get(self, request):
        uid = request.GET.get("uid")
        token = request.GET.get("token")

        if not uid or not token:
            messages.error(request, "Token inválido o expirado.")
            return redirect("tierra_media:register")

        try:
            user = get_user_model().objects.get(pk=uid)
        except get_user_model().DoesNotExist:
            messages.error(request, "El usuario no existe.")
            return redirect("tierra_media:register")

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(
                request,
                "Tu cuenta ha sido activada con éxito. Ahora puedes iniciar sesión.",
            )
            return redirect("tierra_media:login")
        else:
            messages.error(
                request, "El enlace de activación no es válido o ha expirado."
            )
            return redirect("tierra_media:register")


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "tierra_media/index.html"


class NPC_preparations:
    # TODO: create migration with fixed data (factions, locations and races)
    # TODO: faction, location and race need to be an instance of said objects
    def create_npcs():
        npcs = copy.deepcopy(NPCS)
        for npc in npcs:
            npc.update({"character": Character.objects.get(pk=1)})
            # npc_created = NPC(**npc)
            # npc_created.save()


class CharacterCreation(CreateView):
    template_name = "character-creation/character-creation.html"
    form_class = CreateCharacterForm
    success_url = "/tierra-media/character-creation/success/"
    npc = NPC_preparations()

    def check_name(self, form):
        name = form.cleaned_data.get("name")
        # TODO: replace user with session user
        user = form.cleaned_data.get("user")
        if Character.objects.filter(name=name).filter(user=user).exists():
            form.add_error("name", "Ya tienes un personaje con ese nombre.")
            return False
        return True

    def form_valid(self, form):
        if self.check_name(form):
            self.npc.create_npcs()
            return super().form_valid(form)
        return super().form_invalid(form)


class CharacterCreationSuccess(TemplateView):
    template_name = "character-creation/success.html"


class Weapons(UpdateView):
    pass


class Armors(UpdateView):
    pass
