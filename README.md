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

## Descripción

## Estructura

### Settings

---

### Modelos

#### Faction, Location, Race

Modelo para facciones, localizaciones y razas de personajes. Se crean con `name` como único atributo. En un futuro da la posibilidad para expandir sobre esto, añadiendo otros atributos como buffs y debuffs de razas especificas.

---

#### Character

Este modelo tiene todos los atributos del personaje, con su usuario al que pertenece y atributos del personaje (vida, defensa, arma equipada, etc.)

---

#### Weapon, Armor, Backpack

Los modelos de armas y armaduras tienen todos sus detalles, incluyendo el usuario al que pertenecen las armas y armaduras y la mochila a la que pertenece, ya que pueden existir diferentes personajes para un mismo usuario.

### Vistas

#### CharacterCreation

La vista de crear personaje tiene varias funciones dentro de esta, una de ellas, `check_name` que comprueba si el nombre de ese personaje que se va a crear ya existe. Otra de las funciones, `add_icon`, sirve para añadir un icono al personaje dependiendo de su raza.

En esta vista se hace uso del ORM de Django para comprobar si un personaje tiene el mismo nombre. Ademas, esta vista hace uso del atributo `form_class` de `CreateView` para pasarle un formulario creado en un archivo aparte.

---

### Extras

#### Clases \_preparations

Estas clases se encargan de inicializar los NPCs, armas y armaduras. Funcionan las tres que hay de la misma forma, como ejemplo podemos ver como se crean los NPCs.

Por cada npc en el archivo `constants.py` se le asigna a cada uno el objeto de su raza correspondiente, ademas, se le asigna su icono de personaje.

Se hace uso del ORM de Django para encontrar el objeto `Faction` de la facción de ese NPC.

---

#### Django REST Framework

Este proyecto incluye una api utilizando Django REST Framework que devuelve todos los personajes de todos los usuarios. La idea en un futuro es que cuando los personajes ganen batallas se haga un ranking utilizando esa api que muestre en la pagina principal el personaje y su usuario que hayan ganado mas batallas.

## División del trabajo
