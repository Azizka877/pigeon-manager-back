from rest_framework import viewsets
from .models import Reproduction
from .serializers import ReproductionSerializer

class ReproductionViewSet(viewsets.ModelViewSet):
    queryset = Reproduction.objects.all()
    serializer_class = ReproductionSerializer
