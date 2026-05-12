# apps/colombier/apps.py
from django.apps import AppConfig

class ColombierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.colombier'  # ← Chemin Python complet
    verbose_name = 'Configuration Colombier'