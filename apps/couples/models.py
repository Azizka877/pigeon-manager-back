# models
from django.db import models
from django.core.exceptions import ValidationError
import uuid

class Couple(models.Model):
    """
    Modèle représentant un couple de pigeons
    """
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('rompu', 'Rompu'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    male = models.ForeignKey('pigeons.Pigeon', on_delete=models.PROTECT, 
                             related_name='couples_male', limit_choices_to={'sexe': 'M', 'statut': 'actif'})
    femelle = models.ForeignKey('pigeons.Pigeon', on_delete=models.PROTECT, 
                                related_name='couples_femelle', limit_choices_to={'sexe': 'F', 'statut': 'actif'})
    date_formation = models.DateField(auto_now_add=True)
    date_rupture = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='actif')
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Couple"
        verbose_name_plural = "Couples"
        unique_together = [['male', 'femelle', 'statut']]
    
    def __str__(self):
        return f"Couple {self.male.matricule} & {self.femelle.matricule}"
    
    def clean(self):
        """Validation: un pigeon ne peut pas être en couple avec lui-même"""
        if self.male == self.femelle:
            raise ValidationError("Un pigeon ne peut pas former un couple avec lui-même")
    
    def rompre(self, date_rupture=None):
        """Rompre le couple"""
        from django.utils import timezone
        self.statut = 'rompu'
        self.date_rupture = date_rupture or timezone.now().date()
        self.save()
    
    @property
    def est_actif(self):
        return self.statut == 'actif'