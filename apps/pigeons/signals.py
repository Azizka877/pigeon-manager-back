# pigeons/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pigeon
from cages.models import Cage, OccupationCage

@receiver(post_save, sender=Pigeon)
def liberer_cage_si_pigeon_inactif(sender, instance, **kwargs):
    if instance.statut in ['vendu', 'mort', 'perdu']:
        # Trouve et libère la cage occupée par ce pigeon
        occupations = OccupationCage.objects.filter(
            models.Q(pigeon=instance) | 
            models.Q(couple__male=instance) |
            models.Q(couple__femelle=instance),
            date_fin__isnull=True
        )
        for occ in occupations:
            occ.date_fin = timezone.now()
            occ.save()
            occ.cage.statut_actuel = 'libre'
            occ.cage.save()