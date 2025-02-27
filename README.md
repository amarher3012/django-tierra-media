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
4. Ahora podrás usar las distintas funcionalidades del juego con este personaje.

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

#### **IndexView/InfoView/ContactView/ContactSuccess**

Vistas básicas para las páginas de Índice, Información, Contacto y del éxito al enviar un formulario de contacto.

---

#### **AddBackpack**

En esta vista se crea el objeto `Backpack`, que contiene todas las armas del usuario. Esto permite que diferentes personajes tengan diferentes _backpacks_.

#### **CharacterCreation**

Vista para la creación de personajes. Contiene varias funciones, entre ellas:

-   **`check_name`**: Verifica si el nombre del personaje ya existe.
-   **`add_icon`**: Asigna un icono al personaje según su raza.

Se utiliza el ORM de Django para comprobar la existencia de nombres duplicados. Además, se emplea `form_class` de `CreateView` para gestionar los formularios desde un archivo separado.

---

### **Move/MoveSuccess**

Vista que permite que un usuario mueva uno de sus personajes hasta una nueva localización. MoveSuccess muestra una pantalla de éxito con mensajes dinámicos.

---

### **Encounter/EncounterAlly/EncounterNeutral/EncounterEnemy/CombatManager**

Estas vistas se encargan de analizar qué personajes están en la misma localización que el personaje seleccionado y
nos ofrece interactuar con ellos. Si son aliados, habrá una pequeña escena de diálogo en la que estos nos ofrecerán
un ungüento curativo o un arma, si las hubiera disponibles. En el encuentro neutral, se nos permitirá alejarnos o acercarnos al
otro personaje, generando irremediablemente un combate y llevando a la vista de EncounterEnemy.

En EncounterEnemy, se creará una instancia de la clase CombatManager que nos ayudará a manejar toda la lógica del combate.
Esta se mostrará en la plantilla correspondiente en un combate por turnos con animaciones y decisiones en tiempo real que
darán una mayor sensación de estar jugando a un videojuego.

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

#### **Mixin Personalizado**

Mixin personalizado que cuenta con una lista de nombres prohibidos para los personajes creados.

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
- Aportación de ideas para el diseño de la visualización de algunas vistas.
```

### Alexánder Drapala García

```
- Creación y modificación de modelos.
- Creación de armas por defecto para npcs y equiparlas.
- Creación de armaduras por defecto para npcs y equiparlas.
- Implementación de tienda.
- Implementación de listar personajes.
- Implementación de listar las acciones de un personaje.
- Implementación de equipación de objetos, tanto armas como armaduras.
- Implementación de modal para los detalles de los objetos al pasar por encima de estos.
- Búsqueda de iconos para los objetos y algunos fondos.
- Aportación de ideas para el diseño de la visualización de algunas vistas.
```

### Renato R. Romero Valencia

```
- Implementación del diseño.
- Implementación de la lógica del combate.
- Implementación de las relaciones.
- Implementación de mover personajes entre localizaciones.
- Implementacion de Login y Registro.
- Implementación de Validación de Correo
- Implementación de Messages en distintas vistas.
- Implementación de Mixin personalizado.
- Implementación de LoginRequiredMixin.
- Aportación de ideas para el diseño de la visualización de algunas vistas.
```

## 📝 Observaciones adicionales

### Comunicación

Hemos mantenido una comunicación constante durante todo el proyecto a través de distintos medios, como **Discord** (en voz y texto)
o **WhatsApp**. En todo momento hemos sabido cómo estaba avanzando cada uno en sus ramas del proyecto, lo que nos ha evitado muchos
quebraderos de cabeza a la hora de hacer Pull Requests.

### Uso de herramientas de extra

Hemos usado, a lo largo del proyecto, herramientas como **Trello** para organizar el trabajo de una manera directa y dinámica.
También hemos usado herramientas como **pastebin** para compartir *snippets* de código con facilidad y diversos medios para enviarnos
elementos estáticos, como imágenes.

### Cosas que nos hubiera gustado añadir

Hay ciertas cosas que no hemos podido añadir debido a la falta de tiempo.

- Un modelo "Log" que guardase los distintos eventos relacionados con los personajes de un usuario para mostrar los últimos que ocurrieron
y mostrarlos en Inicio.
- Usar la API de REST Framework para tener una especie de ránking en el que se ordenasen a los personajes por sus victorias en combate.
- Implementar "dinero" para los personajes, con los cuales se podría interactuar en la tienda comprando equipamiento y ganándolo tras superar combates o recibirlo
por parte de aliados.
- Que solo se pueda tener encuentros con un aliado concreto una vez cada hora.
- Que los NPCs resucitasen cada día.
- Añadir una especie de objetivos/misiones diarias con los que ganarías más dinero.
- Hacer que la tienda tuviera distintos objetos disponibles dependiendo de su localización y estos estuvieran generados aleatoriamente.
- Conseguir que los objetos de la tienda tengan un límite y se reinicien cada día.

### Roles de cada integrante

- Alejandro: podemos decir que se ha comportado, al igual que en los anteriores trabajos, como el líder del proyecto. Ha establecido
las bases del proyecto con rapidez y, además, ha sido capaz de adaptarse y cambiar gran parte de su trabajo para que encajara mejor con el de los demás. 
No ha permitido que los ánimos decaigan incluso cuando la acumulación de trabajo era notable.

- Alexánder: ha trabajado como nadie y se ha involucrado mucho en la creación de casi todos los elementos del programa. Ha prestado su
ayuda varias veces sin dudarlo para resolver problemas que los otros dos integrantes del equipo estábamos teniendo. Ha demostrado varias
veces su gran habilidad como proofreader y encontrando fallos de manera eficaz cuando los demás no éramos capaces.

- Renato: al igual que en los proyectos anteriores, a Renato se le asignó la tarea de diseñar el sistema de combate, lo que le ha
tomado una cantidad considerable de tiempo. A pesar de eso, ha estado involucrado en la creación de todas las partes del proyecto, 
especialmente en el ámbito creativo donde ha demostrado no dejar de tener ideas. Mucha atención al detalle casi obsesiva.