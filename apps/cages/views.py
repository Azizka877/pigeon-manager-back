from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction

from .models import Cage, Occupation
from .serializers import CageSerializer, OccupationSerializer


class CageViewSet(viewsets.ModelViewSet):
    queryset = Cage.objects.filter(est_active=True)
    serializer_class = CageSerializer
    
    @action(detail=True, methods=['post'])
    def occuper(self, request, pk=None):
        """
        POST /cages/{id}/occuper/
        Body: { pigeon?: string, couple?: string, type_occupation: 'seul' | 'couple' }
        """
        cage = self.get_object()
        
        # Vérifier si la cage est déjà occupée
        occupation_active = cage.occupations.filter(date_fin__isnull=True).first()
        if occupation_active:
            return Response(
                {'detail': 'La cage est déjà occupée'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        type_occupation = request.data.get('type_occupation')
        pigeon_id = request.data.get('pigeon')
        couple_id = request.data.get('couple')
        
        try:
            with transaction.atomic():
                occupation = Occupation.objects.create(
                    cage=cage,
                    type_occupation=type_occupation,
                    pigeon_id=pigeon_id if type_occupation == 'seul' else None,
                    couple_id=couple_id if type_occupation == 'couple' else None,
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
        
        # Mettre fin à l'occupation
        occupation.date_fin = timezone.now()
        occupation.save()
        
        return Response(
            {'detail': 'Cage libérée avec succès'}, 
            status=status.HTTP_200_OK
        )