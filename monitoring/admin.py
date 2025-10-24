from django.contrib import admin
from .models import Filtre, Capteur, Salle

@admin.register(Filtre)
class FiltreAdmin(admin.ModelAdmin):
    list_display = ['nom', 'salle', 'broche_esp32', 'vitesse', 'actif']
    list_editable = ['broche_esp32', 'vitesse', 'actif']
    list_filter = ['salle', 'actif']
    search_fields = ['nom', 'localisation']

@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ['nom']

@admin.register(Capteur)
class CapteurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type', 'valeur', 'filtre']
    list_filter = ['type', 'filtre']
    search_fields = ['nom', 'type']