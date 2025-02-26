# Tierra Media con Django

```
                                              ________________________
    _______________________-------------------                       `|
  /:--__                                                              |
  ||< > |                                   ___________________________/
  | |__/_________________-------------------                         |
  |                                                                  |
  |                       EL SEÑOR DE LOS ANILLOS                     |
  |                                                                  |
  |      Tres anillos para los Reyes Elfos bajo el cielo,            |
    |        Siete para los Señores Enanos en sus salas de piedra,     |
    |      Nueve para los Hombres Mortales condenados a morir,         |
    |        Uno para el Señor Oscuro en su oscuro trono               |
    |      En la Tierra de Mordor donde yacen las Sombras.              |
    | Un Anillo para gobernarlos a todos, Un Anillo para encontrarlos, |
    |       Un Anillo para traerlos a todos y en la oscuridad unirlos. |
    |     En la Tierra de Mordor donde yacen las Sombras.              |
    |                                              ____________________|_
    |  ___________________-------------------------                      `|
    |/`--_                                                                 |
    ||[ ]||                                            ___________________/
    |===/___________________--------------------------
```

## 📜 Descripción

Este es un proyecto inspirado en _El Señor de los Anillos_, desarrollado con Django, Bootstrap y algo de JavaScript para cosas visuales. Sus funcionalidades incluyen:

-   Moverse a través de las diferentes localizaciones.
-   Elegir y equipar armas y armaduras.
-   Tener encuentros aliados, neutrales y enemigos.
-   Crear varios personajes.
-   API para mostrar datos de personajes.

## 📚 Guía

Pasos básicos para comenzar a jugar:

1. Crear un usuario con un correo electrónico válido.
2. Activar la cuenta mediante el enlace de confirmación enviado por correo.
3. Iniciar sesión y crear un personaje.

## 📂 Estructura

El proyecto sigue la estructura básica de Django con una sola aplicación (`tierra_media`).

```
django-tierra-media
├── config/
├── static/
├── templates/
│   ├── 404.html
│   ├── registration/
│   └── base.html
├── tierra_media/
│   ├── migrations/
│   ├── templates/
│   │   ├── character-creation/
│   │   ├── encounters/
│   │   ├── move/
│   │   ├── nav/
│   │   ├── tierra_media/
│   │   └── weapons/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── constants.py
│   ├── forms.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── README.md
└── requirements.txt
```

### 🔧 Configuración

Se han instalado diversas aplicaciones en `INSTALLED_APPS`, entre ellas:

-   **Django Bootstrap**: Para aplicar estilos de Bootstrap.
-   **Django REST Framework**: Para la creación de APIs.
-   **Debug Toolbar**: Para herramientas de depuración.

Además, en este archivo se configuran las credenciales necesarias para la verificación por correo electrónico, almacenadas en `.env`.

---

### 🗄️ Modelos

#### **Faction, Location, Race**

Modelo para facciones, ubicaciones y razas de personajes. Se crean con `name` como único atributo. En el futuro, podrían incluir atributos adicionales como _buffs_ y _debuffs_ específicos de cada raza.

#### **Character**

Modelo que contiene los atributos del personaje, el usuario al que pertenece y estadísticas como vida, defensa y arma equipada.

#### **Weapon, Armor, Backpack**

Los modelos de armas y armaduras contienen sus detalles específicos e incluyen una relación con el usuario propietario y la mochila a la que pertenecen. Un usuario puede tener varios personajes con distintos equipos.

---

### 🖥️ Vistas

#### **RegisterView**

Vista para el registro de usuarios. Se asigna un token y se construye la URL de verificación por correo.

---

#### **ActivateAccount**

Esta vista se encarga de activar al usuario una vez se haga clic en el enlace enviado al correo. `user.is_active` se convierte en `True` si el token es válido. Luego, se crean los NPCs del usuario junto con las armas y armaduras disponibles para este.

---

#### **IndexView/InfoView/ContactView**

Vistas básicas para las páginas de Índice, Información y Contacto.

---

#### **AddBackpack**

En esta vista se crea el objeto `Backpack`, que contiene todas las armas del usuario. Esto permite que diferentes personajes tengan diferentes _backpacks_.

#### **CharacterCreation**

Vista para la creación de personajes. Contiene varias funciones, entre ellas:

-   **`check_name`**: Verifica si el nombre del personaje ya existe.
-   **`add_icon`**: Asigna un icono al personaje según su raza.

Se utiliza el ORM de Django para comprobar la existencia de nombres duplicados. Además, se emplea `form_class` de `CreateView` para gestionar los formularios desde un archivo separado.

---

### 🛠️ Extras

#### **Clases \\\_preparations**

Estas clases inicializan NPCs, armas y armaduras de manera similar. Por ejemplo, para los NPCs:

1. Se asigna la raza correspondiente desde `constants.py`.
2. Se asigna un icono de personaje.
3. Se usa el ORM de Django para vincular la facción de cada NPC.

---

#### **Django REST Framework**

El proyecto incluye una API con Django REST Framework que devuelve todos los personajes de los usuarios. En el futuro, se usará para crear un ranking de personajes basado en el número de batallas ganadas, que se mostrará en la página principal.

---

#### **Tests**

Se han realizado pruebas básicas para verificar el flujo principal del juego:

1. Creación de usuario.
2. Creación de personaje.
3. Acceso a `index.html`.
4. Validación de la existencia del personaje.
5. Movimiento del personaje.

## 🤝 División del trabajo

### Alejandro Martín Herrera

```
- Estructura del proyecto
- Creación de modelos
- Creación de personajes
- Implementación de NPCs
- Implementación de iconos para personajes, armas y armaduras
- Implementación de API con Django REST Framework
- Tests
```

### Alexánder Drapala García

```
(Pendiente de completar)
```

### Renato R. Romero Valencia

```
(Pendiente de completar)
```
