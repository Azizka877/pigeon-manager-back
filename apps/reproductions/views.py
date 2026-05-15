from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Reproduction
from .serializers import (
    ReproductionSerializer,
    ReproductionCreateSerializer,
    ReproductionUpdateSerializer,
)


class ReproductionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les reproductions.
    
    Endpoints:
    - GET /api/reproductions/ — Liste
    - POST /api/reproductions/ — Créer (avec jeunes optionnels)
    - GET /api/reproductions/{id}/ — Détail
    - PUT/PATCH /api/reproductions/{id}/ — Modifier
    - DELETE /api/reproductions/{id}/ — Supprimer
    - POST /api/reproductions/{id}/ajouter-jeunes/ — Ajouter des jeunes
    """
    
    queryset = Reproduction.objects.all().select_related(
        'couple', 'couple__male', 'couple__femelle'
    ).prefetch_related('jeunes')
    
    def get_serializer_class(self):
        """Choisir le serializer selon l'action"""
        if self.action == 'create':
            return ReproductionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReproductionUpdateSerializer
        return ReproductionSerializer
    
    def get_queryset(self):
        """Filtrer les reproductions"""
        queryset = super().get_queryset()
        
        # Filtre par couple
        couple = self.request.query_params.get('couple')
        if couple:
            queryset = queryset.filter(couple_id=couple)
        
        # Filtre par statut
        statut = self.request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        # Filtre par date
        date_debut = self.request.query_params.get('date_debut')
        date_fin = self.request.query_params.get('date_fin')
        if date_debut:
            queryset = queryset.filter(date_ponte__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_ponte__lte=date_fin)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def ajouter_jeunes(self, request, pk=None):
        """
        POST /api/reproductions/{id}/ajouter-jeunes/
        
        Ajouter des jeunes à une reproduction existante.
        """
        reproduction = self.get_object()
        
        serializer = JeuneDataSerializer(data=request.data.get('jeunes', []), many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            jeunes_crees = reproduction.creer_jeunes(serializer.validated_data)
            for jeune in jeunes_crees:
                reproduction.jeunes.add(jeune)
            
            return Response({
                'message': f'{len(jeunes_crees)} jeune(s) ajouté(s)',
                'jeunes': PigeonMiniSerializer(jeunes_crees, many=True).data
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def arbre(self, request, pk=None):
        """
        GET /api/reproductions/{id}/arbre/
        
        Retourne l'arbre généalogique du couple de cette reproduction.
        """
        reproduction = self.get_object()
        couple = reproduction.couple
        
        if not couple or not couple.male or not couple.femelle:
            return Response(
                {'error': 'Couple incomplet'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        arbre_male = couple.male.get_arbre(profondeur=2) if hasattr(couple.male, 'get_arbre') else None
        arbre_femelle = couple.femelle.get_arbre(profondeur=2) if hasattr(couple.femelle, 'get_arbre') else None
        
        return Response({
            'reproduction_id': str(reproduction.id),
            'couple': {
                'male': {
                    'id': str(couple.male.id),
                    'matricule': couple.male.matricule,
                    'arbre': arbre_male,
                },
                'femelle': {
                    'id': str(couple.femelle.id),
                    'matricule': couple.femelle.matricule,
                    'arbre': arbre_femelle,
                },
            },
            'jeunes': PigeonMiniSerializer(reproduction.jeunes.all(), many=True).data,
        })