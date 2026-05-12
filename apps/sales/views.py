from rest_framework import viewsets
from .models import Sortie
from .serializers import SortieSerializer

class SortieViewSet(viewsets.ModelViewSet):
    queryset = Sortie.objects.all()
    serializer_class = SortieSerializer
