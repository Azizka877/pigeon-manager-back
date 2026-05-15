# apps/pigeons/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import Pigeon
from .serializers import PigeonSerializer, PigeonEventSerializer


class PigeonViewSet(viewsets.ModelViewSet):
    queryset = Pigeon.objects.filter(deleted_at__isnull=True)
    serializer_class = PigeonSerializer
    
    def get_queryset(self):
        queryset = Pigeon.objects.filter(deleted_at__isnull=True)
        
        # Filtre par statut
        statut = self.request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        # Filtre par sexe
        sexe = self.request.query_params.get('sexe')
        if sexe:
            queryset = queryset.filter(sexe=sexe)
        
        # Filtre par race
        race = self.request.query_params.get('race')
        if race:
            queryset = queryset.filter(race__icontains=race)
        
        # Recherche par matricule
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(matricule__icontains=search)
        
        return queryset.select_related('pere', 'mere').prefetch_related('events')
    
    @action(detail=True, methods=['get', 'post'])
    def events(self, request, pk=None):
        pigeon = self.get_object()
        
        if request.method == 'GET':
            events = pigeon.events.all().order_by('-date')
            serializer = PigeonEventSerializer(events, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = PigeonEventSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(pigeon=pigeon)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # === ENDPOINTS GÉNÉALOGIE ===
    
    @action(detail=True, methods=['get'])
    def arbre(self, request, pk=None):
        """
        GET /api/pigeons/{id}/arbre/?profondeur=3
        
        Retourne l'arbre généalogique du pigeon.
        """
        pigeon = self.get_object()
        profondeur = int(request.query_params.get('profondeur', 3))
        
        # Limiter la profondeur pour éviter les requêtes trop lourdes
        profondeur = min(profondeur, 5)
        
        arbre = pigeon.get_arbre(profondeur)
        
        return Response({
            'pigeon': {
                'id': str(pigeon.id),
                'matricule': pigeon.matricule,
                'sexe': pigeon.get_sexe_display(),
                'generation': pigeon.generation,
            },
            'arbre': arbre,
            'profondeur': profondeur
        })
    
    @action(detail=True, methods=['get'])
    def freres_soeurs(self, request, pk=None):
        """
        GET /api/pigeons/{id}/freres-soeurs/
        
        Retourne les frères et sœurs du même couple parental.
        """
        pigeon = self.get_object()
        freres = pigeon.get_freres_soeurs()
        
        serializer = PigeonSerializer(freres, many=True)
        return Response({
            'count': freres.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def descendants(self, request, pk=None):
        """
        GET /api/pigeons/{id}/descendants/
        
        Retourne tous les descendants du pigeon.
        """
        pigeon = self.get_object()
        descendants = pigeon.get_descendants()
        
        # Sérialiser manuellement
        data = []
        for desc in descendants:
            data.append({
                'niveau': desc['niveau'],
                'relation': desc['relation'],
                'pigeon': {
                    'id': str(desc['pigeon'].id),
                    'matricule': desc['pigeon'].matricule,
                    'sexe': desc['pigeon'].get_sexe_display(),
                    'generation': desc['pigeon'].generation,
                }
            })
        
        return Response({
            'count': len(data),
            'results': data
        })
    
    @action(detail=True, methods=['get'])
    def parents(self, request, pk=None):
        """
        GET /api/pigeons/{id}/parents/
        
        Retourne les parents directs du pigeon.
        """
        pigeon = self.get_object()
        
        return Response({
            'pere': {
                'id': str(pigeon.pere.id) if pigeon.pere else None,
                'matricule': pigeon.pere.matricule if pigeon.pere else None,
                'sexe': pigeon.pere.get_sexe_display() if pigeon.pere else None,
            } if pigeon.pere else None,
            'mere': {
                'id': str(pigeon.mere.id) if pigeon.mere else None,
                'matricule': pigeon.mere.matricule if pigeon.mere else None,
                'sexe': pigeon.mere.get_sexe_display() if pigeon.mere else None,
            } if pigeon.mere else None,
        })