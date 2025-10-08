from rest_framework import viewsets
from .models import Filtre, Capteur
from .serializers import FiltreSerializer, CapteurSerializer

class FiltreViewSet(viewsets.ModelViewSet):
    queryset = Filtre.objects.all()
    serializer_class = FiltreSerializer

class CapteurViewSet(viewsets.ModelViewSet):
    queryset = Capteur.objects.all()
    serializer_class = CapteurSerializer