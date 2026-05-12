from rest_framework import serializers
from .models import Couple
from apps.pigeons.serializers import PigeonSerializer

class CoupleSerializer(serializers.ModelSerializer):
    male_details = PigeonSerializer(source='male', read_only=True)
    femelle_details = PigeonSerializer(source='femelle', read_only=True)
    
    class Meta:
        model = Couple
        fields = ['id', 'male', 'male_details', 'femelle', 'femelle_details', 
                  'date_formation', 'date_rupture', 'statut', 'notes']
