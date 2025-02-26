from django.contrib import messages
from django.shortcuts import redirect

class ForbiddenNamesMixin:
    """
    Mixin para evitar la creación de personajes con nombres prohibidos.
    Compara los nombres independientemente de mayúsculas/minúsculas.
    """
    # Lista de nombres prohibidos
    forbidden_names = [
        'frodo', 'aragorn', 'legolas', 'gimli', 'sauron',
        'saruman', 'JavaScript', 'Hitler', 'Franco'
    ]

    # Nombre del campo a validar (por defecto 'name')
    name_field = 'name'

    # URL a la que redirigir en caso de nombre prohibido
    # Si es None, se usa el referer o 'tierra_media:index'
    redirect_url = None

    # Mensaje de error personalizado
    error_message = "El nombre '{name}' no está permitido para un personaje."

    def form_valid(self, form):
        """
        Valida el formulario antes de guardarlo.
        Comprueba si el nombre del personaje está en la lista de nombres prohibidos.
        """
        # Obtener el valor del campo de nombre del formulario
        character_name = form.cleaned_data.get(self.name_field, '')

        # Comprobar si el nombre está en la lista de prohibidos (ignorando mayúsculas)
        for forbidden_name in self.forbidden_names:
            if character_name.lower() == forbidden_name.lower():
                # Mostrar mensaje de error
                messages.error(
                    self.request,
                    self.error_message.format(name=character_name)
                )

                # Determinar a dónde redirigir
                if self.redirect_url:
                    return redirect(self.redirect_url)
                elif self.request.META.get('HTTP_REFERER'):
                    return redirect(self.request.META.get('HTTP_REFERER'))
                else:
                    return redirect('tierra_media:index')

        # Si el nombre no está prohibido, continuar con el flujo normal
        return super().form_valid(form)