# apps/cages/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction

from .models import Cage, Occupation, HistoriqueCage
from .serializers import CageSerializer, OccupationSerializer, HistoriqueCageSerializer


class CageViewSet(viewsets.ModelViewSet):
    queryset = Cage.objects.filter(est_active=True)
    serializer_class = CageSerializer
    
    @action(detail=True, methods=['post'])
    def occuper(self, request, pk=None):
        cage = self.get_object()
        
        occupation_active = cage.occupations.filter(date_fin__isnull=True).first()
        if occupation_active:
            return Response(
                {'detail': 'La cage est déjà occupée'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        type_occupation = request.data.get('type_occupation')
        pigeon_id = request.data.get('pigeon_id')      # ✅ Corrigé : 'pigeon_id' au lieu de 'pigeon'
        couple_id = request.data.get('couple_id')      # ✅ Corrigé : 'couple_id' au lieu de 'couple'
        
        try:
            with transaction.atomic():
                occupation = Occupation.objects.create(
                    cage=cage,
                    type_occupation=type_occupation,
                    pigeon_id=pigeon_id if type_occupation == 'seul' else None,
                    couple_id=couple_id if type_occupation == 'couple' else None,
                )
                
                # CRÉER L'HISTORIQUE
                HistoriqueCage.objects.create(
                    cage=cage,
                    type_action='occupation',
                    description=f'Cage {cage.numero} occupée ({type_occupation})',
                    utilisateur=request.user,
                    metadata={
                        'type_occupation': type_occupation,
                        'pigeon_id': pigeon_id,
                        'couple_id': couple_id,
                    }
                )
                
                serializer = OccupationSerializer(occupation)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post', 'delete'])
    def liberer(self, request, pk=None):
        """
        POST ou DELETE /cages/{id}/liberer/
        """
        cage = self.get_object()
        
        # Trouver l'occupation active
        occupation = cage.occupations.filter(date_fin__isnull=True).first()
        
        if not occupation:
            return Response(
                {'detail': 'La cage est déjà libre'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Sauvegarder les infos avant suppression
        type_occupation = occupation.type_occupation
        pigeon_id = str(occupation.pigeon.id) if occupation.pigeon else None
        couple_id = str(occupation.couple.id) if occupation.couple else None
        
        # Mettre fin à l'occupation
        occupation.date_fin = timezone.now()
        occupation.save()
        
        # CRÉER L'HISTORIQUE
        HistoriqueCage.objects.create(
            cage=cage,
            type_action='liberation',
            description=f'Cage {cage.numero} libérée',
            utilisateur=request.user,
            metadata={
                'type_occupation': type_occupation,
                'pigeon_id': pigeon_id,
                'couple_id': couple_id,
            }
        )
        
        return Response(
            {'detail': 'Cage libérée avec succès'}, 
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def historique(self, request, pk=None):
        """GET /cages/{id}/historique/"""
        cage = self.get_object()
        historiques = cage.historiques.all()[:50]
        serializer = HistoriqueCageSerializer(historiques, many=True)
        return Response(serializer.data)