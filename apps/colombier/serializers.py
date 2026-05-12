# apps/colombier/serializers.py
from rest_framework import serializers
from .models import ColombierConfig

class ColombierConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColombierConfig
        fields = ['id', 'nom', 'pays', 'ville', 'gps', 'proprietaire', 'created_at', 'updated_at']
        read_only_fields = ['id', 'proprietaire', 'created_at', 'updated_at']