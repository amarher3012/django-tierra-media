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
-   Conseguir armas y armaduras en la tienda.
-   Elegir y equipar armas y armaduras.
-   Tener encuentros aliados, neutrales y enemigos.
-   Crear varios personajes.
-   API para mostrar datos de personajes.

## 📚 Guía

Pasos básicos para comenzar a jugar:

1. Instalar proyecto.
2. Realizar migraciones (`makemigrations` y `migrate`).
3. Crear superusuario (`createsuperuser`).
4. Crear un archivo .env con la variable que contiene la contraseña de aplicación del correo electrónico (consultar email enviado por Renato).
5. Instalar todo el contenido de requirements.txt.
6. Crear un usuario con un correo electrónico válido.
7. Activar la cuenta mediante el enlace de confirmación enviado por correo.
8. Iniciar sesión y crear un personaje.
9. Ahora podrás usar las distintas funcionalidades del juego con este personaje.

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

#### **IndexView/InfoView/ContactView/ContactSuccess/About**

Vistas básicas para las páginas de Índice, Información, Contacto y del éxito al enviar un formulario de contacto y la página de "Sobre Nosotros".

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

### **Mostrar relaciones**

En la propia vista de CharacterDetails se encuentra la lógica detrás de cómo se establecen las relaciones entre los personajes. Se hace una comparación y dependiendo de su facción la vista devuelve tres listas con todos los aliados, enemigos y neutrales.
Esta se mostrará en el navegador como un modal.

---

### **Encounter/EncounterAlly/EncounterNeutral/EncounterEnemy/CombatManager**

Estas vistas se encargan de analizar qué personajes están en la misma localización que el personaje seleccionado y
nos ofrece interactuar con ellos. Si son aliados, habrá una pequeña escena de diálogo en la que estos nos ofrecerán
un ungüento curativo o un arma, si las hubiera disponibles. En el encuentro neutral, se nos permitirá alejarnos o acercarnos al
otro personaje, generando irremediablemente un combate y llevando a la vista de EncounterEnemy.

En EncounterEnemy, se creará una instancia de la clase CombatManager que nos ayudará a manejar toda la lógica del combate.
Esta se mostrará en la plantilla correspondiente en un combate por turnos con animaciones y decisiones en tiempo real que
darán una mayor sensación de estar jugando a un videojuego.

#### ⚔️ **Combate*

De estas vistas la más compleja es el combate.

Cuando se entra a un combate, lo primero que realizará la vista será cargar la plantilla de enemy.html. Cogerá como contexto al personaje usado, al enemigo y un booleano que indicará si el usuario tiene un arma equipada.
A continuación, en la función "post" vamos a (con un try-except) a cargar el objeto Character, su nombre, su vida máxima y su defensa.
Haremos lo mismo con el enemigo. Estas son las estadísticas que necesitamos para calcular el combate. Se envían respuestas JsonResponse para poder enviar la suficiente información para mostrarle al usuario de manera sencilla lo que está ocurriendo.

Se determina la acción elegida por el jugador ("Atacar", "Defender" o "Huir").

Cada turno de combate llama a la función "CombatManager". Se creará una instancia de turno de combate y se calcularán los resultados de este usando la lógica del combate.

Entonces actualiza los puntos de salud de ambos contrincantes y su defensa (en caso de que se defendiese, lo cual hace que la defensa aumente y luego vuelva a su estado natural).

En caso de que el combate termine, se maneja la eliminación del personaje eliminado (si lo hubiera) y lo borra de la base de datos.

En CombatManager, cada turno, se inicializa la instancia con referencias del personaje usado y el enemigo.

Lo primero que se realizará en cada tunro es resetear la defensa, que podría haber sido aumentada en el turno anterior, a su estado natural. Luego, se verifica si los personajes
tienen algún arma equipada, ya que en caso contrario perderían automáticamente el enfrentamiento y serían eliminados. Esto se maneja antes de que se realice ninguna acción para que no dé pie a errores.

Los bonos raciales son los siguientes:

| Raza    | Iniciativa | Multiplicador de Daño | Multiplicador de Defensa | Probabilidad de Huida | Crítico |
|---------|------------|------------------------|--------------------------|------------------------|---------|
| Humano  | +5         | 1.20 (+20%)            | 1.0                      | 0                      | 0       |
| Elfo    | +20        | 1.10 (+10%)            | 1.0                      | 0                      | +15%    |
| Enano   | 0          | 1.10 (+10%)            | 1.20 (+20%)              | 0                      | 0       |
| Hobbit  | +15        | 1.0                    | 1.0                      | +20%                   | 0       |
| Orco    | 0          | 1.50 (+50%)            | 1.0                      | 0                      | 0       |

Aunque estamos manejando una variable que es la iniciativa, al final tuvimos que desecharla por cuestión de tiempo. Para simplificar el proceso, el personaje del usuario siempre actuará primero.

Si el personaje ataca, lo primero será comprobar si el defensor está desarmado (victoria automática). Luego si tiene una defensa crítica (anula todo el daño que pueda recibir). Calculamos entonces el daño del personaje utilizado usando la fuerza del arma equipada multiplicada por 2.5 +
10 (para ajustar el daño un poco) y aplicamos los bonificadores raciales pertinentes. 

A este daño le aplicamos la reducción de daño del enemigo (la cual se calcula a partir de su defensa y la suma de su armadura equipada, si la tuviese). Se le aplica el multiplicador en caso de que sea enano y tenga defensa mejorada. 

Entonces, calculamos el porcentaje de defensa dividiendo la defensa entre 250, con un tope máximo del 75% para no crear personajes inmunes al daño. Si el defensor está en posición defensiva, aplicamos un reductor adicional al daño. Finalmente, calculamos el daño definitivo como el daño
del arma menos la defensa porcentual (mínimo 1 para evitar ataques que no hagan nada).

Para añadir variabilidad y sorpresa al combate, aplicamos un modificador aleatorio entre -10% y +30%. También se calcula si el ataque es crítico, basado en la probabilidad base del 15% más los bonos raciales (por ejemplo, los elfos tienen un 15% adicional). En caso de crítico, el daño se
multiplica por 1.5.

Si el personaje logra derrotar al enemigo, se elimina al enemigo de la base de datos y se notifica la victoria. Si no, el enemigo contraataca siguiendo el mismo proceso, y se verifica si el personaje es derrotado.

Si el personaje elige defenderse, aumenta significativamente su defensa para ese turno. Tiene una probabilidad del 25% + (defensa × 0.12) de lograr una defensa crítica, que anula completamente cualquier daño recibido. Si realiza una defensa normal, reduce el daño entrante en un 60%. Tras
la defensa, el enemigo decide si atacar (más probable) o también defenderse (si tiene poca salud). Se calculan los resultados y se comprueba si algún combatiente ha sido derrotado.

Si el personaje intenta huir, la probabilidad base es del 50%, modificada por los bonos raciales (los hobbits tienen +20%) y reducida en un 20% si el oponente es un orco. Si la huida tiene éxito, el combate termina inmediatamente. Si falla, el enemigo ataca automáticamente, siguiendo el
mismo proceso de cálculo de daño explicado anteriormente.

En cada turno, el sistema devuelve información detallada: la acción realizada, un mensaje descriptivo del resultado, una etiqueta para el estilo del mensaje (peligro, advertencia, éxito), el resultado final (victoria, derrota o huida), y los cambios en salud y estado de los personajes.
Esta información permite que la interfaz se actualice adecuadamente para mostrar lo ocurrido en el turno.

Tras cada combate, los personajes derrotados son eliminados permanentemente de la base de datos, implementando así un sistema de muerte permanente que añade tensión y consecuencias reales a cada enfrentamiento.

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
- Implementación de Mixin personalizado.
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
- Implementación de Validación de Correo.
- Implementación de Messages en distintas vistas y cómo se muestran.
- Implementación de Mixin personalizado.
- Implementación de LoginRequiredMixin.
- Implementación de vistas "Información", "Contacto" y "Sobre Nosotros".
- Implementación de formulario de contacto que los envía a la cuenta de correo de contacto.
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
