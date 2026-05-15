from rest_framework import serializers
from .models import Reproduction
from apps.pigeons.serializers import PigeonMiniSerializer


# ─── Serializer pour les données des jeunes à créer ───
class JeuneDataSerializer(serializers.Serializer):
    """Données pour créer un pigeonneau lors d'une reproduction"""
    matricule = serializers.CharField(max_length=50)
    sexe = serializers.ChoiceField(choices=[('M', 'Mâle'), ('F', 'Femelle')])
    couleur = serializers.CharField(max_length=50, required=False, allow_blank=True)
    race = serializers.CharField(max_length=100, required=False, allow_blank=True)


# ─── Serializer pour la lecture (GET / liste) ───
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
                'id': str(obj.couple.male.id) if obj.couple.male else None,
                'matricule': obj.couple.male.matricule if obj.couple.male else None,
                'race': obj.couple.male.race if obj.couple.male else None,
            },
            'femelle': {
                'id': str(obj.couple.femelle.id) if obj.couple.femelle else None,
                'matricule': obj.couple.femelle.matricule if obj.couple.femelle else None,
                'race': obj.couple.femelle.race if obj.couple.femelle else None,
            },
        }
    
    def get_jeunes_details(self, obj):
        """Détails des jeunes liés"""
        return PigeonMiniSerializer(obj.jeunes.all(), many=True).data


# ─── Serializer pour la création (POST) avec jeunes ───
class ReproductionCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une reproduction avec des jeunes"""
    jeunes = JeuneDataSerializer(many=True, required=False, write_only=True)
    
    class Meta:
        model = Reproduction
        fields = [
            'couple', 'date_ponte', 'date_eclosion',
            'nombre_oeufs', 'notes', 'jeunes'
        ]
    
    def validate(self, data):
        """Validation personnalisée"""
        jeunes = data.get('jeunes', [])
        
        # Vérifier les matricules uniques
        matricules = [j['matricule'] for j in jeunes if j.get('matricule')]
        if len(matricules) != len(set(matricules)):
            raise serializers.ValidationError("Les matricules des jeunes doivent être uniques")
        
        # Vérifier que le couple est actif
        couple = data.get('couple')
        if couple and hasattr(couple, 'statut') and couple.statut != 'actif':
            raise serializers.ValidationError("Le couple sélectionné n'est pas actif")
        
        return data
    
    def create(self, validated_data):
        """Créer la reproduction et les jeunes associés"""
        jeunes_data = validated_data.pop('jeunes', [])
        
        # Créer la reproduction
        reproduction = Reproduction.objects.create(**validated_data)
        
        # Créer les jeunes et les lier
        if jeunes_data:
            try:
                jeunes_crees = reproduction.creer_jeunes(jeunes_data)
                # Ajouter à la relation ManyToMany
                for jeune in jeunes_crees:
                    reproduction.jeunes.add(jeune)
            except ValueError as e:
                # Si un matricule existe déjà, supprimer la reproduction et lever l'erreur
                reproduction.delete()
                raise serializers.ValidationError(str(e))
        
        return reproduction


# ─── Serializer pour la mise à jour (PUT/PATCH) ───
class ReproductionUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour une reproduction"""
    jeunes = JeuneDataSerializer(many=True, required=False, write_only=True)
    
    class Meta:
        model = Reproduction
        fields = [
            'date_ponte', 'date_eclosion', 'date_sevrage',
            'nombre_oeufs', 'nombre_eclos', 'nombre_jeunes',
            'statut', 'notes', 'jeunes'
        ]
    
    def update(self, instance, validated_data):
        """Mettre à jour la reproduction et ajouter des jeunes si fournis"""
        jeunes_data = validated_data.pop('jeunes', None)
        
        # Mise à jour des champs standards
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Ajouter de nouveaux jeunes si fournis
        if jeunes_data:
            try:
                jeunes_crees = instance.creer_jeunes(jeunes_data)
                for jeune in jeunes_crees:
                    instance.jeunes.add(jeune)
            except ValueError as e:
                raise serializers.ValidationError(str(e))
        
        return instance