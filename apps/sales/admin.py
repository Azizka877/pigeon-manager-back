from django.contrib import admin
from .models import Sortie

@admin.register(Sortie)
class SortieAdmin(admin.ModelAdmin):
    list_display = ['pigeon', 'type_sortie', 'date_sortie', 'prix', 'acheteur']
    list_filter = ['type_sortie', 'date_sortie']
    search_fields = ['pigeon__matricule', 'acheteur']
    readonly_fields = ['id', 'created_at']
    fieldsets = (
        ('Sortie', {
            'fields': ('pigeon', 'type_sortie', 'date_sortie')
        }),
        ('Vente', {
            'fields': ('prix', 'acheteur'),
            'classes': ('collapse',)
        }),
        ('Décès/Perte', {
            'fields': ('cause', 'circonstances'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
