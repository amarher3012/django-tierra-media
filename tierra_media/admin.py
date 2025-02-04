from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register([Character, Faction, Location, Race, Backpack, Weapon, Armor])
