from django.db import models

from django.db import models

class Filtre(models.Model):
    nom = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    date_installation = models.DateField()
    localisation = models.CharField(max_length=100)
    actif = models.BooleanField(default=True)

class Capteur(models.Model):
    filtre = models.OneToOneField(Filtre, on_delete=models.CASCADE, related_name='capteur')
    type = models.CharField(max_length=50)
    valeur = models.FloatField()
