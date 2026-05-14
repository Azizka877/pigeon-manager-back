# apps/dashboard/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta, datetime, date
import logging

from apps.cages.models import HistoriqueCage
from apps.pigeons.models import Pigeon
from apps.couples.models import Couple
from apps.reproductions.models import Reproduction
from apps.sales.models import Sortie

logger = logging.getLogger(__name__)

MAX_LIMIT = 100  # Cap absolu pour éviter les requêtes folles


def safe_get(obj, attr, default=None):
    """Récupère un attribut en toute sécurité."""
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default


def to_datetime(d):
    """Uniformise n'importe quelle date en datetime aware."""
    if d is None:
        return timezone.now()
    if isinstance(d, str):
        # Parse ISO string
        try:
            d = d.replace('Z', '+00:00')
            return datetime.fromisoformat(d)
        except Exception:
            return timezone.now()
    if isinstance(d, date) and not isinstance(d, datetime):
        return timezone.make_aware(datetime.combine(d, datetime.min.time()))
    if isinstance(d, datetime) and timezone.is_naive(d):
        return timezone.make_aware(d)
    return d


@api_view(['GET'])
def activites_recentes(request):
    """
    GET /api/activites/?limit=10&days=30
    
    Retourne les activités récentes du colombier.
    """
    try:
        # --- Validation des paramètres ---
        try:
            limit = int(request.query_params.get('limit', 10))
        except (ValueError, TypeError):
            limit = 10
        
        limit = min(max(limit, 1), MAX_LIMIT)  # Clamp entre 1 et MAX_LIMIT
        
        try:
            days = int(request.query_params.get('days', 30))
        except (ValueError, TypeError):
            days = 30
        
        depuis = timezone.now() - timedelta(days=max(days, 1))
        activites = []
        
        # ============================================
        # 1. HISTORIQUE DES CAGES
        # ============================================
        try:
            historiques = HistoriqueCage.objects.select_related(
                'cage', 'utilisateur'
            ).filter(
                date_action__gte=depuis
            ).order_by('-date_action')[:limit]
            
            for h in historiques:
                cage_numero = safe_get(h.cage, 'numero', h.cage_id) if h.cage else h.cage_id
                activites.append({
                    'id': f'hist-{h.id}',
                    'type': 'cage',
                    'type_action': safe_get(h, 'type_action', 'action'),
                    'titre': f'Cage {cage_numero} - {safe_get(h, "type_action", "action")}',
                    'description': safe_get(h, 'description', '') or f'Action sur cage {cage_numero}',
                    'date': to_datetime(safe_get(h, 'date_action')).isoformat(),
                    'utilisateur': safe_get(h.utilisateur, 'username') if h.utilisateur else None,
                    'metadata': safe_get(h, 'metadata') or {},
                })
        except Exception as e:
            logger.error(f"[activites] Erreur historique cages: {e}")
        
        # ============================================
        # 2. NOUVEAUX PIGEONS
        # ============================================
        try:
            nouveaux_pigeons = Pigeon.objects.filter(
                created_at__gte=depuis
            ).order_by('-created_at')[:limit]
            
            for p in nouveaux_pigeons:
                matricule = safe_get(p, 'matricule', str(p.id))
                race = safe_get(p, 'race', '')
                
                # Gestion sécurisée du sexe
                sexe_display = '?'
                try:
                    if hasattr(p, 'get_sexe_display'):
                        sexe_display = p.get_sexe_display()
                    else:
                        sexe_display = safe_get(p, 'sexe', '?')
                except Exception:
                    sexe_display = safe_get(p, 'sexe', '?')
                
                activites.append({
                    'id': f'pigeon-{p.id}',
                    'type': 'pigeon',
                    'type_action': 'creation',
                    'titre': f'Nouveau pigeon {matricule}',
                    'description': f'{matricule} - {race} ({sexe_display})',
                    'date': to_datetime(safe_get(p, 'created_at')).isoformat(),
                    'utilisateur': None,
                    'metadata': {
                        'matricule': matricule,
                        'sexe': safe_get(p, 'sexe'),
                    },
                })
        except Exception as e:
            logger.error(f"[activites] Erreur pigeons: {e}")
        
        # ============================================
        # 3. NOUVEAUX COUPLES
        # ============================================
        try:
            # Vérifie si le champ date_formation existe
            if hasattr(Couple, 'date_formation'):
                nouveaux_couples = Couple.objects.filter(
                    date_formation__gte=depuis
                ).order_by('-date_formation')[:limit]
            else:
                # Fallback sur created_at si pas de date_formation
                nouveaux_couples = Couple.objects.filter(
                    created_at__gte=depuis
                ).order_by('-created_at')[:limit]
            
            for c in nouveaux_couples:
                male = safe_get(c, 'male', '?')
                femelle = safe_get(c, 'femelle', '?')
                
                # Détermine la date à utiliser
                date_couple = safe_get(c, 'date_formation') or safe_get(c, 'created_at')
                
                activites.append({
                    'id': f'couple-{c.id}',
                    'type': 'couple',
                    'type_action': 'formation',
                    'titre': 'Nouveau couple formé',
                    'description': f'{male} + {femelle}',
                    'date': to_datetime(date_couple).isoformat(),
                    'utilisateur': None,
                    'metadata': {
                        'male': str(male),
                        'femelle': str(femelle),
                    },
                })
        except Exception as e:
            logger.error(f"[activites] Erreur couples: {e}")
        
        # ============================================
        # 4. NOUVELLES REPRODUCTIONS
        # ============================================
        try:
            if hasattr(Reproduction, 'date_ponte'):
                nouvelles_repros = Reproduction.objects.filter(
                    date_ponte__gte=depuis
                ).order_by('-date_ponte')[:limit]
            else:
                nouvelles_repros = Reproduction.objects.filter(
                    created_at__gte=depuis
                ).order_by('-created_at')[:limit]
            
            for r in nouvelles_repros:
                # Récupère l'ID du couple (couple_id ou couple.id)
                couple_id = safe_get(r, 'couple_id')
                if couple_id is None and hasattr(r, 'couple') and r.couple:
                    couple_id = r.couple.id
                
                date_repro = safe_get(r, 'date_ponte') or safe_get(r, 'created_at')
                
                activites.append({
                    'id': f'repro-{r.id}',
                    'type': 'reproduction',
                    'type_action': 'debut',
                    'titre': 'Nouvelle reproduction',
                    'description': f'Couple {couple_id or "?"}',
                    'date': to_datetime(date_repro).isoformat(),
                    'badge': 'Repro',
                })
        except Exception as e:
            logger.error(f"[activites] Erreur reproductions: {e}")
        
        # ============================================
        # 5. SORTIES RÉCENTES
        # ============================================
        try:
            if hasattr(Sortie, 'date_sortie'):
                sorties_recentes = Sortie.objects.filter(
                    date_sortie__gte=depuis
                ).order_by('-date_sortie')[:limit]
            else:
                sorties_recentes = Sortie.objects.filter(
                    created_at__gte=depuis
                ).order_by('-created_at')[:limit]
            
            for s in sorties_recentes:
                type_sortie = safe_get(s, 'type_sortie', 'sortie')
                
                # Construction de la description
                if type_sortie == 'vente':
                    acheteur = safe_get(s, 'acheteur', 'Inconnu')
                    prix = safe_get(s, 'prix')
                    description = f'Vendu à {acheteur}'
                    if prix:
                        description += f' ({prix}€)'
                else:
                    description = safe_get(s, 'cause') or safe_get(s, 'circonstances') or 'Sortie enregistrée'
                
                # Type display
                type_display = type_sortie
                try:
                    if hasattr(s, 'get_type_sortie_display'):
                        type_display = s.get_type_sortie_display()
                except Exception:
                    pass
                
                date_sortie = safe_get(s, 'date_sortie') or safe_get(s, 'created_at')
                
                activites.append({
                    'id': f'sortie-{s.id}',
                    'type': 'sortie',
                    'type_action': type_sortie,
                    'titre': f'Pigeon {type_display}',
                    'description': description,
                    'date': to_datetime(date_sortie).isoformat(),
                    'badge': type_sortie,
                })
        except Exception as e:
            logger.error(f"[activites] Erreur sorties: {e}")
        
        # ============================================
        # TRI ET RÉPONSE
        # ============================================
        activites.sort(key=lambda x: to_datetime(x['date']), reverse=True)
        activites = activites[:limit]
        
        return Response({
            'count': len(activites),
            'results': activites
        })
        
    except Exception as e:
        logger.exception("[activites] Erreur globale non gérée")
        return Response(
            {
                'error': 'Erreur serveur',
                'detail': str(e),
                'count': 0,
                'results': []
            },
            status=500
        )