# models
from django.db import models
import uuid
from django.utils import timezone
from django.conf import settings

class Cage(models.Model):
    """
    Modèle représentant une cage dans la volière
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=10, unique=True, verbose_name="Numéro de cage")
    nom = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nom")
    superficie = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, verbose_name="Superficie (m²)")
    position_x = models.IntegerField(default=0, verbose_name="Position X (grille)")
    position_y = models.IntegerField(default=0, verbose_name="Position Y (grille)")
    est_active = models.BooleanField(default=True, verbose_name="Cage active")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cage"
        verbose_name_plural = "Cages"
        ordering = ['numero']
    
    def __str__(self):
        return f"Cage {self.numero}"
    
    @property
    def statut_actuel(self):
        """Retourne le statut actuel de la cage: libre, seul, couple"""
        occupation = self.occupations.filter(date_fin__isnull=True).first()
        if not occupation:
            return 'libre'
        if occupation.couple:
            return 'couple'
        return 'seul'
    
    @property
    def occupation_actuelle(self):
        """Retourne l'occupation actuelle de la cage"""
        return self.occupations.filter(date_fin__isnull=True).first()


class Occupation(models.Model):
    """
    Modèle pour suivre l'occupation des cages (historique)
    """
    TYPE_CHOICES = [
        ('seul', 'Pigeon seul'),
        ('couple', 'Couple'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cage = models.ForeignKey(Cage, on_delete=models.CASCADE, related_name='occupations')
    pigeon = models.ForeignKey('pigeons.Pigeon', on_delete=models.CASCADE, null=True, blank=True)
    couple = models.ForeignKey('couples.Couple', on_delete=models.CASCADE, null=True, blank=True)
    type_occupation = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Occupation"
        verbose_name_plural = "Occupations"
        ordering = ['-date_debut']
    
    def __str__(self):
        if self.type_occupation == 'seul' and self.pigeon:
            return f"{self.cage.numero} - {self.pigeon.matricule}"
        elif self.type_occupation == 'couple' and self.couple:
            return f"{self.cage.numero} - Couple {self.couple.id}"
        return f"{self.cage.numero} - Libre"
    
    def liberer(self):
        """Libère la cage"""
        self.date_fin = timezone.now()
        self.save()



class HistoriqueCage(models.Model):
    TYPE_ACTION = [
        ('occupation', 'Occupation'),
        ('liberation', 'Libération'),
        ('nettoyage', 'Nettoyage'),
        ('creation', 'Création'),
        ('modification', 'Modification'),
    ]
    
    cage = models.ForeignKey('Cage', on_delete=models.CASCADE, related_name='historiques')
    type_action = models.CharField(max_length=20, choices=TYPE_ACTION)
    description = models.TextField()
    date_action = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # Données supplémentaires (JSON pour flexibilité)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-date_action']
    
    def __str__(self):
        return f"{self.cage.numero} - {self.type_action} - {self.date_action}"