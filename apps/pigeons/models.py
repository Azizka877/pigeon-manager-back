# models
from django.db import models
import uuid
from django.utils import timezone

class Pigeon(models.Model):
    """
    Modèle représentant un pigeon dans la volière
    """
    SEXE_CHOICES = [
        ('M', 'Mâle'),
        ('F', 'Femelle'),
    ]
    
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('vendu', 'Vendu'),
        ('mort', 'Mort'),
        ('perdu', 'Perdu'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    matricule = models.CharField(max_length=50, unique=True, verbose_name="Matricule (bague)")
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, verbose_name="Sexe")
    race = models.CharField(max_length=100, verbose_name="Race")
    date_naissance = models.DateField(verbose_name="Date de naissance")
    couleur = models.CharField(max_length=50, blank=True, null=True, verbose_name="Couleur")
    poids = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Poids (g)")
    
    # Relations familiales
    pere = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                             related_name='enfants_pere', verbose_name="Père")
    mere = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                             related_name='enfants_mere', verbose_name="Mère")
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif', verbose_name="Statut")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    
    # Dates système
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Soft delete
    
    class Meta:
        verbose_name = "Pigeon"
        verbose_name_plural = "Pigeons"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['matricule']),
            models.Index(fields=['statut']),
            models.Index(fields=['sexe']),
        ]
    
    def __str__(self):
        return f"{self.matricule} - {self.get_sexe_display()} - {self.race}"
    
    def soft_delete(self):
        """Soft delete - marque comme supprimé sans supprimer de la base"""
        self.deleted_at = timezone.now()
        self.save()
    
    @property
    def est_actif(self):
        return self.statut == 'actif' and self.deleted_at is None
    
    @property
    def age(self):
        """Calcule l'âge en années"""
        from datetime import date
        today = date.today()
        return today.year - self.date_naissance.year - (
            (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
        )
        
        

class PigeonEvent(models.Model):
    TYPE_CHOICES = [
        ('medical', 'Médical'),
        ('vaccination', 'Vaccination'),
        ('reproduction', 'Reproduction'),
        ('concours', 'Concours'),
        ('autre', 'Autre'),
    ]
    
    pigeon = models.ForeignKey(Pigeon, on_delete=models.CASCADE, related_name='events')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date = models.DateField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']