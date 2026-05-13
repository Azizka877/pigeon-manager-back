from rest_framework import serializers
from .models import Pigeon, PigeonEvent

class PigeonSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    sexe_display = serializers.CharField(source='get_sexe_display', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    
    class Meta:
        model = Pigeon
        fields = [
            'id', 'matricule', 'sexe', 'sexe_display', 'race', 
            'date_naissance', 'age', 'couleur', 'poids',
            'pere', 'mere', 'statut', 'statut_display',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_age(self, obj):
        """Calculer l'âge du pigeon"""
        from datetime import date
        if obj.date_naissance:
            today = date.today()
            age = today.year - obj.date_naissance.year
            if (today.month, today.day) < (obj.date_naissance.month, obj.date_naissance.day):
                age -= 1
            return age
        return None



class PigeonEventSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = PigeonEvent
        fields = ['id', 'pigeon', 'type', 'type_display', 'date', 'description', 'created_at']
        read_only_fields = ['created_at']
