# apps/reproductions/models.py
from django.db import models
import uuid
from django.utils import timezone

class Reproduction(models.Model):
    """
    Modèle pour enregistrer les reproductions/naissances
    """
    STATUT_CHOICES = [
        ('incubation', 'Incubation'),
        ('eclosion', 'Éclosion'),
        ('sevrage', 'Sevrage'),
        ('termine', 'Terminé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    couple = models.ForeignKey('couples.Couple', on_delete=models.PROTECT, related_name='reproductions')
    date_ponte = models.DateField(verbose_name="Date de ponte")
    date_eclosion = models.DateField(verbose_name="Date d'éclosion", null=True, blank=True)
    date_sevrage = models.DateField(verbose_name="Date de sevrage", null=True, blank=True)
    nombre_oeufs = models.IntegerField(default=2, verbose_name="Nombre d'oeufs")
    nombre_eclos = models.IntegerField(default=0, verbose_name="Nombre d'éclos")
    nombre_jeunes = models.IntegerField(default=0, verbose_name="Nombre de jeunes nés")
    
    # === LIENS VERS LES JEUNES CRÉÉS ===
    jeunes = models.ManyToManyField(
        'pigeons.Pigeon', 
        related_name='naissances', 
        blank=True,
        verbose_name="Pigeonneaux bagués"
    )
    
    notes = models.TextField(blank=True, null=True)
    
    # Auto-calcul du statut
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='incubation',
        verbose_name="Statut"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Reproduction"
        verbose_name_plural = "Reproductions"
        ordering = ['-date_ponte']
    
    def __str__(self):
        return f"Reproduction {self.couple} - {self.date_ponte}"
    
    def save(self, *args, **kwargs):
        # Auto-calcul du statut basé sur les dates
        today = timezone.now().date()
        
        if self.date_sevrage and today >= self.date_sevrage:
            self.statut = 'termine'
        elif self.date_eclosion and today >= self.date_eclosion:
            self.statut = 'sevrage'
        elif self.date_ponte:
            jours = (today - self.date_ponte).days
            if jours >= 17:
                self.statut = 'eclosion'
            else:
                self.statut = 'incubation'
        
        super().save(*args, **kwargs)
    
    def creer_jeunes(self, donnees_jeunes):
        """
        Crée les pigeonneaux et les lie à cette reproduction.
        
        donnees_jeunes = [
            {'matricule': 'P011', 'sexe': 'M', 'couleur': 'Bleu', 'race': 'Voyageur'},
            {'matricule': 'P012', 'sexe': 'F', 'couleur': 'Rouge', 'race': 'Voyageur'},
        ]
        """
        from apps.pigeons.models import Pigeon
        
        jeunes_crees = []
        pere = self.couple.male
        mere = self.couple.femelle
        
        # Calcul de la génération
        generation_parent = max(
            getattr(pere, 'generation', 0),
            getattr(mere, 'generation', 0)
        )
        
        for data in donnees_jeunes:
            # Vérifie que le matricule n'existe pas déjà
            if Pigeon.objects.filter(matricule=data['matricule']).exists():
                raise ValueError(f"Le matricule {data['matricule']} existe déjà")
            
            jeune = Pigeon.objects.create(
                matricule=data['matricule'],
                sexe=data.get('sexe', 'M'),
                race=data.get('race', pere.race),
                couleur=data.get('couleur', ''),
                date_naissance=self.date_eclosion or self.date_ponte,
                pere=pere,
                mere=mere,
                generation=generation_parent + 1,
                origine='ne',
                statut='actif'
            )
            self.jeunes.add(jeune)
            jeunes_crees.append(jeune)
        
        self.nombre_jeunes = self.jeunes.count()
        self.save()
        
        return jeunes_crees
    
    @property
    def jeunes_details(self):
        """Retourne les détails des jeunes liés"""
        return self.jeunes.all()