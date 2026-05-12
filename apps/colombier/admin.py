# apps/colombier/admin.py
from django.contrib import admin
from .models import ColombierConfig

@admin.register(ColombierConfig)
class ColombierConfigAdmin(admin.ModelAdmin):
    list_display = ['nom', 'pays', 'ville', 'proprietaire', 'created_at']
    list_filter = ['pays', 'created_at']
    search_fields = ['nom', 'ville', 'proprietaire__username']
    readonly_fields = ['created_at', 'updated_at']