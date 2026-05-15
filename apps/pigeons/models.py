# apps/pigeons/models.py
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
    
    # === GÉNÉALOGIE ===
    pere = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='enfants_pere', 
        verbose_name="Père"
    )
    mere = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='enfants_mere', 
        verbose_name="Mère"
    )
    generation = models.PositiveIntegerField(default=0, verbose_name="Génération")
    
    # Origine (né ici ou acheté)
    ORIGINE_CHOICES = [
        ('ne', 'Né dans le colombier'),
        ('achete', 'Acheté'),
        ('don', 'Don'),
        ('echange', 'Échange'),
    ]
    origine = models.CharField(max_length=20, choices=ORIGINE_CHOICES, default='ne', verbose_name="Origine")
    
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
            models.Index(fields=['generation']),
            models.Index(fields=['pere']),
            models.Index(fields=['mere']),
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
    
    @property
    def parents(self):
        """Retourne le couple parental"""
        return (self.pere, self.mere)
    
    def get_freres_soeurs(self):
        """Retourne les frères et sœurs du même couple parental"""
        if self.pere and self.mere:
            return Pigeon.objects.filter(
                pere=self.pere,
                mere=self.mere,
                deleted_at__isnull=True
            ).exclude(id=self.id)
        return Pigeon.objects.none()
    
    def get_grands_parents(self):
        """Retourne les grands-parents"""
        grands_parents = []
        if self.pere:
            if self.pere.pere:
                grands_parents.append(('paternel', 'pere', self.pere.pere))
            if self.pere.mere:
                grands_parents.append(('paternel', 'mere', self.pere.mere))
        if self.mere:
            if self.mere.pere:
                grands_parents.append(('maternel', 'pere', self.mere.pere))
            if self.mere.mere:
                grands_parents.append(('maternel', 'mere', self.mere.mere))
        return grands_parents
    
    def get_arbre(self, profondeur=3):
        """Construit l'arbre généalogique récursivement"""
        if profondeur <= 0:
            return None
        
        arbre = {
            'id': str(self.id),
            'matricule': self.matricule,
            'sexe': self.get_sexe_display(),
            'generation': self.generation,
            'date_naissance': self.date_naissance,
        }
        
        if self.pere and profondeur > 1:
            arbre['pere'] = self.pere.get_arbre(profondeur - 1)
        else:
            arbre['pere'] = None
            
        if self.mere and profondeur > 1:
            arbre['mere'] = self.mere.get_arbre(profondeur - 1)
        else:
            arbre['mere'] = None
        
        return arbre
    
    def get_descendants(self, niveau=0, max_niveau=5):
        """Retourne tous les descendants (enfants, petits-enfants...)"""
        if niveau >= max_niveau:
            return []
        
        descendants = []
        # Enfants où ce pigeon est le père
        enfants_pere = self.enfants_pere.filter(deleted_at__isnull=True)
        # Enfants où ce pigeon est la mère
        enfants_mere = self.enfants_mere.filter(deleted_at__isnull=True)
        
        # Union des deux querysets
        from django.db.models import Q
        enfants = Pigeon.objects.filter(
            Q(pere=self) | Q(mere=self),
            deleted_at__isnull=True
        ).distinct()
        
        for enfant in enfants:
            descendants.append({
                'niveau': niveau + 1,
                'relation': 'enfant',
                'pigeon': enfant
            })
            descendants.extend(enfant.get_descendants(niveau + 1, max_niveau))
        
        return descendants


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