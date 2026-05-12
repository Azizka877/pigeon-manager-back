# models
from django.db import models
import uuid

class Reproduction(models.Model):
    """
    Modèle pour enregistrer les reproductions/naissances
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    couple = models.ForeignKey('couples.Couple', on_delete=models.PROTECT, related_name='reproductions')
    date_ponte = models.DateField(verbose_name="Date de ponte")
    date_eclosion = models.DateField(verbose_name="Date d'éclosion")
    nombre_oeufs = models.IntegerField(default=2, verbose_name="Nombre d'oeufs")
    nombre_jeunes = models.IntegerField(default=0, verbose_name="Nombre de jeunes nés")
    jeunes = models.ManyToManyField('pigeons.Pigeon', related_name='naissances', blank=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Reproduction"
        verbose_name_plural = "Reproductions"
        ordering = ['-date_ponte']
    
    def __str__(self):
        return f"Reproduction {self.couple} - {self.date_ponte}"