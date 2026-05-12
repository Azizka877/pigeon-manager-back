from django.contrib import admin
from .models import Reproduction

@admin.register(Reproduction)
class ReproductionAdmin(admin.ModelAdmin):
    list_display = ['couple', 'date_ponte', 'date_eclosion', 'nombre_jeunes']
    list_filter = ['date_ponte']
    search_fields = ['couple__male__matricule', 'couple__femelle__matricule']
    readonly_fields = ['id', 'created_at', 'updated_at']
    filter_horizontal = ['jeunes']
