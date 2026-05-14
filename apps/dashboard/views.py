# apps/dashboard/views.py (nouveau fichier)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from apps.cages.models import HistoriqueCage
from apps.pigeons.models import Pigeon
from apps.couples.models import Couple
from apps.reproductions.models import Reproduction
from apps.sales.models import Sortie

@api_view(['GET'])
def activites_recentes(request):
    """GET /api/activites/?limit=10"""
    limit = int(request.query_params.get('limit', 10))
    
    activites = []
    
    # 1. Historique des cages (occupations/libérations)
    historiques = HistoriqueCage.objects.select_related('cage', 'utilisateur').order_by('-date_action')[:limit]
    for h in historiques:
        activites.append({
            'id': f'hist-{h.id}',
            'type': 'cage',
            'type_action': h.type_action,  # 'occupation' ou 'liberation'
            'titre': f'Cage {h.cage.numero} - {h.type_action}',
            'description': h.description,
            'date': h.date_action,
            'utilisateur': h.utilisateur.username if h.utilisateur else None,
            'metadata': h.metadata,
        })
    
    # 2. Nouveaux pigeons (derniers 7 jours)
    depuis = timezone.now() - timedelta(days=7)
    nouveaux_pigeons = Pigeon.objects.filter(created_at__gte=depuis).order_by('-created_at')[:limit]
    for p in nouveaux_pigeons:
        activites.append({
            'id': f'pigeon-{p.id}',
            'type': 'pigeon',
            'type_action': 'creation',
            'titre': f'Nouveau pigeon {p.matricule}',
            'description': f'{p.matricule} - {p.race} ({p.get_sexe_display()})',
            'date': p.created_at,
            'utilisateur': None,
            'metadata': {'matricule': p.matricule, 'sexe': p.sexe},
        })
    
    # 3. Nouveaux couples
    nouveaux_couples = Couple.objects.filter(date_formation__gte=depuis).order_by('-date_formation')[:limit]
    for c in nouveaux_couples:
        activites.append({
            'id': f'couple-{c.id}',
            'type': 'couple',
            'type_action': 'formation',
            'titre': f'Nouveau couple formé',
            'description': f'{c.male_details.matricule} + {c.femelle_details.matricule}',
            'date': c.date_formation,
            'utilisateur': None,
            'metadata': {'male': c.male, 'femelle': c.femelle},
        })
    
    # 4. Nouvelles reproductions
    nouvelles_repros = Reproduction.objects.filter(date_debut__gte=depuis).order_by('-date_debut')[:limit]
    for r in nouvelles_repros:
        activites.append({
            'id': f'repro-{r.id}',
            'type': 'reproduction',
            'type_action': 'debut',
            'titre': f'Nouvelle reproduction',
            'description': f'Couple {r.couple_id}',
            'date': r.date_debut,
            'utilisateur': None,
            'metadata': {'couple_id': str(r.couple_id)},
        })
    
    # 5. Sorties (ventes, pertes, décès)
    sorties = Sortie.objects.filter(date_sortie__gte=depuis).order_by('-date_sortie')[:limit]
    for s in sorties:
        activites.append({
            'id': f'sortie-{s.id}',
            'type': 'sortie',
            'type_action': s.type_sortie,  # 'vente', 'perte', 'deces'
            'titre': f'Pigeon {s.type_sortie}',
            'description': f'{s.pigeon.matricule} - {s.motif or ""}',
            'date': s.date_sortie,
            'utilisateur': None,
            'metadata': {'prix': s.prix, 'acheteur': s.acheteur},
        })
    
    # Trier par date décroissante et limiter
    activites.sort(key=lambda x: x['date'], reverse=True)
    activites = activites[:limit]
    
    return Response({
        'count': len(activites),
        'results': activites
    })