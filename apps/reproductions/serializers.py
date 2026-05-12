from rest_framework import serializers
from .models import Reproduction

class ReproductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reproduction
        fields = '__all__'
