from rest_framework import serializers
from .models import Filtre, Capteur

class CapteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Capteur
        fields = '__all__'

class FiltreSerializer(serializers.ModelSerializer):
    capteur = CapteurSerializer(read_only=True)

    class Meta:
        model = Filtre
        fields = '__all__'