from rest_framework import viewsets
from .models import Pigeon
from .serializers import PigeonSerializer

class PigeonViewSet(viewsets.ModelViewSet):
    queryset = Pigeon.objects.filter(deleted_at__isnull=True)
    serializer_class = PigeonSerializer
