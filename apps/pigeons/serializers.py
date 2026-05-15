from rest_framework import serializers
from .models import Pigeon, PigeonEvent


class PigeonEventSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = PigeonEvent
        fields = ['id', 'pigeon', 'type', 'type_display', 'date', 'description', 'created_at']
        read_only_fields = ['created_at']


class PigeonMiniSerializer(serializers.ModelSerializer):
    """Serializer léger pour les références parentales"""
    sexe_display = serializers.CharField(source='get_sexe_display', read_only=True)
    
    class Meta:
        model = Pigeon
        fields = ['id', 'matricule', 'sexe', 'sexe_display', 'race', 'couleur', 'generation']


class PigeonSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    sexe_display = serializers.CharField(source='get_sexe_display', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    origine_display = serializers.CharField(source='get_origine_display', read_only=True)
    
    # === GÉNÉALOGIE ===
    pere_details = serializers.SerializerMethodField()
    mere_details = serializers.SerializerMethodField()
    freres_soeurs = serializers.SerializerMethodField()
    grands_parents = serializers.SerializerMethodField()
    enfants = serializers.SerializerMethodField()
    
    class Meta:
        model = Pigeon
        fields = [
            'id', 'matricule', 'sexe', 'sexe_display', 'race', 
            'date_naissance', 'age', 'couleur', 'poids',
            'generation', 'origine', 'origine_display',
            'pere', 'mere', 'pere_details', 'mere_details',
            'freres_soeurs', 'grands_parents', 'enfants',
            'statut', 'statut_display', 'notes',
            'created_at', 'updated_at'
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
    
    def get_pere_details(self, obj):
        """Détails du père"""
        if obj.pere:
            return {
                'id': str(obj.pere.id),
                'matricule': obj.pere.matricule,
                'sexe': obj.pere.get_sexe_display(),
                'race': obj.pere.race,
                'generation': obj.pere.generation,
            }
        return None
    
    def get_mere_details(self, obj):
        """Détails de la mère"""
        if obj.mere:
            return {
                'id': str(obj.mere.id),
                'matricule': obj.mere.matricule,
                'sexe': obj.mere.get_sexe_display(),
                'race': obj.mere.race,
                'generation': obj.mere.generation,
            }
        return None
    
    def get_freres_soeurs(self, obj):
        """Frères et sœurs du même couple parental"""
        freres = obj.get_freres_soeurs()
        return [
            {
                'id': str(f.id),
                'matricule': f.matricule,
                'sexe': f.get_sexe_display(),
                'race': f.race,
                'date_naissance': f.date_naissance,
            }
            for f in freres
        ]
    
    def get_grands_parents(self, obj):
        """Grands-parents"""
        grands = obj.get_grands_parents()
        return [
            {
                'cote': g[0],  # 'paternel' ou 'maternel'
                'lien': g[1],  # 'pere' ou 'mere'
                'id': str(g[2].id),
                'matricule': g[2].matricule,
                'race': g[2].race,
            }
            for g in grands
        ]
    
    def get_enfants(self, obj):
        """Enfants directs"""
        from django.db.models import Q
        enfants = Pigeon.objects.filter(
            Q(pere=obj) | Q(mere=obj),
            deleted_at__isnull=True
        ).distinct()
        
        return [
            {
                'id': str(e.id),
                'matricule': e.matricule,
                'sexe': e.get_sexe_display(),
                'race': e.race,
                'date_naissance': e.date_naissance,
                'generation': e.generation,
            }
            for e in enfants
        ]