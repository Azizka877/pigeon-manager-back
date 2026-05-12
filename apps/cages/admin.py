from django.contrib import admin
from .models import Cage, Occupation

@admin.register(Cage)
class CageAdmin(admin.ModelAdmin):
    list_display = ['numero', 'nom', 'superficie', 'est_active', 'statut_actuel']
    list_filter = ['est_active']
    search_fields = ['numero', 'nom']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def statut_actuel(self, obj):
        return obj.statut_actuel
    statut_actuel.short_description = 'Statut actuel'

@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    list_display = ['cage', 'type_occupation', 'date_debut', 'date_fin']
    list_filter = ['type_occupation']
    readonly_fields = ['id', 'date_debut']
