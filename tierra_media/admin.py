from django.contrib import admin
from .models import *


admin.site.register(
    [
        Character,
        Faction,
        Location,
        Relationship,
        Race,
        UniqueWeapon,
        UniqueArmor,
        CommonWeapon,
        CommonArmor,
    ]
)
