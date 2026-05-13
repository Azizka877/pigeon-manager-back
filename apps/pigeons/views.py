from rest_framework import viewsets
from rest_framework.decorators import action
from .models import Pigeon, PigeonEvent
from .serializers import PigeonSerializer, PigeonEventSerializer

class PigeonViewSet(viewsets.ModelViewSet):
    queryset = Pigeon.objects.filter(deleted_at__isnull=True)
    serializer_class = PigeonSerializer
    
    
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
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)