from rest_framework import serializers
from .models import Reproduction
from apps.pigeons.serializers import PigeonMiniSerializer


class ReproductionSerializer(serializers.ModelSerializer):
    couple_details = serializers.SerializerMethodField()
    jeunes_details = serializers.SerializerMethodField()
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    
    class Meta:
        model = Reproduction
        fields = [
            'id', 'couple', 'couple_details',
            'date_ponte', 'date_eclosion', 'date_sevrage',
            'nombre_oeufs', 'nombre_eclos', 'nombre_jeunes',
            'jeunes', 'jeunes_details',
            'statut', 'statut_display', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_couple_details(self, obj):
        """Détails du couple"""
        return {
            'id': str(obj.couple.id),
            'male': {
                'id': str(obj.couple.male.id),
                'matricule': obj.couple.male.matricule,
                'race': obj.couple.male.race,
            } if obj.couple.male else None,
            'femelle': {
                'id': str(obj.couple.femelle.id),
                'matricule': obj.couple.femelle.matricule,
                'race': obj.couple.femelle.race,
            } if obj.couple.femelle else None,
        }
    
    def get_jeunes_details(self, obj):
        """Détails des jeunes liés"""
        return PigeonMiniSerializer(obj.jeunes.all(), many=True).data