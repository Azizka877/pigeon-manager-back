# apps/colombier/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ColombierConfig
from .serializers import ColombierConfigSerializer

class ColombierConfigViewSet(viewsets.ModelViewSet):
    serializer_class = ColombierConfigSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retourne uniquement le colombier de l'utilisateur connecté"""
        return ColombierConfig.objects.filter(proprietaire=self.request.user)

    def get_object(self):
        """
        Retourne le colombier de l'utilisateur ou en crée un nouveau
        """
        queryset = self.get_queryset()
        obj = queryset.first()
        
        if obj is None:
            # Créer un colombier par défaut pour l'utilisateur
            obj = ColombierConfig.objects.create(
                proprietaire=self.request.user,
                nom='Grand Horizon Lofts',
                pays='Netherlands',
                ville='Amsterdam'
            )
        
        return obj

    def list(self, request, *args, **kwargs):
        """Override list pour retourner un seul objet (pas une liste)"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Créer un colombier pour l'utilisateur"""
        # Vérifier si l'utilisateur a déjà un colombier
        existing = ColombierConfig.objects.filter(proprietaire=request.user).first()
        if existing:
            return Response(
                {'detail': 'Vous avez déjà un colombier configuré.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(proprietaire=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Mettre à jour le colombier de l'utilisateur"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Empêcher la suppression du colombier"""
        return Response(
            {'detail': 'La suppression du colombier n\'est pas autorisée.'},
            status=status.HTTP_403_FORBIDDEN
        )