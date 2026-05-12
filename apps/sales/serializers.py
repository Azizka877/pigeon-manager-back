from rest_framework import serializers
from .models import Sortie

class SortieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sortie
        fields = '__all__'
