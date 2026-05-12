from rest_framework import serializers
from .models import Cage, Occupation
from apps.pigeons.serializers import PigeonSerializer
from apps.couples.serializers import CoupleSerializer

class CageSerializer(serializers.ModelSerializer):
    statut_actuel = serializers.SerializerMethodField()
    occupation_actuelle = serializers.SerializerMethodField()
    
    class Meta:
        model = Cage
        fields = [
            'id', 'numero', 'nom', 'superficie', 
            'position_x', 'position_y', 'est_active',
            'statut_actuel', 'occupation_actuelle',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_statut_actuel(self, obj):
        return obj.statut_actuel
    
    def get_occupation_actuelle(self, obj):
        occupation = obj.occupations.filter(date_fin__isnull=True).first()
        if occupation:
            return {
                'type': occupation.type_occupation,
                'date_debut': occupation.date_debut,
                'pigeon': PigeonSerializer(occupation.pigeon).data if occupation.pigeon else None,
                'couple': CoupleSerializer(occupation.couple).data if occupation.couple else None
            }
        return None

class OccupationSerializer(serializers.ModelSerializer):
    cage_numero = serializers.CharField(source='cage.numero', read_only=True)
    pigeon_details = PigeonSerializer(source='pigeon', read_only=True)
    couple_details = CoupleSerializer(source='couple', read_only=True)
    
    class Meta:
        model = Occupation
        fields = [
            'id', 'cage', 'cage_numero', 'pigeon', 'pigeon_details',
            'couple', 'couple_details', 'type_occupation',
            'date_debut', 'date_fin'
        ]
        read_only_fields = ['id', 'date_debut']
