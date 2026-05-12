from rest_framework import viewsets
from .models import Couple
from .serializers import CoupleSerializer

class CoupleViewSet(viewsets.ModelViewSet):
    queryset = Couple.objects.filter(statut='actif')
    serializer_class = CoupleSerializer
