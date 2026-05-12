from django.db import models
import uuid

class Sortie(models.Model):
    """
    Modèle pour gérer les sorties des pigeons (vente, décès, perte)
    """
    TYPE_CHOICES = [
        ('vente', 'Vente'),
        ('deces', 'Décès'),
        ('perte', 'Perte'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pigeon = models.ForeignKey('pigeons.Pigeon', on_delete=models.PROTECT, related_name='sorties')
    type_sortie = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date_sortie = models.DateField()
    
    # Pour les ventes
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    acheteur = models.CharField(max_length=200, blank=True, null=True)
    
    # Pour les décès et pertes
    cause = models.TextField(blank=True, null=True)
    circonstances = models.TextField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Sortie"
        verbose_name_plural = "Sorties"
        ordering = ['-date_sortie']
    
    def __str__(self):
        return f"{self.pigeon.matricule} - {self.get_type_sortie_display()} - {self.date_sortie}"
    
    def save(self, *args, **kwargs):
        """À la création d'une sortie, mettre à jour le statut du pigeon"""
        super().save(*args, **kwargs)
        
        # Mettre à jour le statut du pigeon selon le type de sortie
        if self.type_sortie == 'vente':
            self.pigeon.statut = 'vendu'
        elif self.type_sortie == 'deces':
            self.pigeon.statut = 'mort'
        elif self.type_sortie == 'perte':
            self.pigeon.statut = 'perdu'
        self.pigeon.save()