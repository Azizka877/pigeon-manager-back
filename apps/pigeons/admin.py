from django.contrib import admin
from .models import Pigeon

@admin.register(Pigeon)
class PigeonAdmin(admin.ModelAdmin):
    list_display = ['matricule', 'sexe', 'race', 'date_naissance', 'statut', 'created_at']
    list_filter = ['sexe', 'race', 'statut']
    search_fields = ['matricule', 'race']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'matricule', 'sexe', 'race')
        }),
        ('Naissance', {
            'fields': ('date_naissance', 'couleur', 'poids')
        }),
        ('Généalogie', {
            'fields': ('pere', 'mere')
        }),
        ('Statut', {
            'fields': ('statut', 'notes')
        }),
        ('Dates système', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
