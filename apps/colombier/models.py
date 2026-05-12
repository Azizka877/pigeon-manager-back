# apps/colombier/models.py
from django.db import models
from django.contrib.auth.models import User

class ColombierConfig(models.Model):
    nom = models.CharField(
        max_length=200, 
        default='Mon Colombier',
        verbose_name='Nom du colombier'
    )
    pays = models.CharField(
        max_length=100, 
        default='Senegal',
        verbose_name='Pays'
    )
    ville = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='Ville / Région'
    )
    gps = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='Coordonnées GPS'
    )
    proprietaire = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='colombier',
        verbose_name='Propriétaire'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'colombier_config'
        verbose_name = 'Configuration du colombier'
        verbose_name_plural = 'Configurations des colombiers'

    def __str__(self):
        return f"{self.nom} ({self.proprietaire.username})"