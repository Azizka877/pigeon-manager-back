from rest_framework import viewsets
from .models import Cage
from .serializers import CageSerializer

class CageViewSet(viewsets.ModelViewSet):
    queryset = Cage.objects.filter(est_active=True)
    serializer_class = CageSerializer
