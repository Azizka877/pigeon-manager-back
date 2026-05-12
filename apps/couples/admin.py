from django.contrib import admin
from .models import Couple

@admin.register(Couple)
class CoupleAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'date_formation', 'statut']
    list_filter = ['statut']
    search_fields = ['male__matricule', 'femelle__matricule']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Couple', {
            'fields': ('male', 'femelle')
        }),
        ('Période', {
            'fields': ('date_formation', 'date_rupture')
        }),
        ('Statut', {
            'fields': ('statut', 'notes')
        }),
    )
