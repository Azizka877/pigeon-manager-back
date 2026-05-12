from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Désenregistrer le modèle User par défaut
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    # Ajouter des champs supplémentaires si vous avez étendu User
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': (),
            'classes': ('collapse',)
        }),
    )
