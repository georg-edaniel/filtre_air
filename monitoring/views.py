from django.shortcuts import render
from rest_framework import viewsets
from .models import Filtre, Capteur
from .serializers import FiltreSerializer, CapteurSerializer
from django.shortcuts import redirect, get_object_or_404

class FiltreViewSet(viewsets.ModelViewSet):
    queryset = Filtre.objects.all()
    serializer_class = FiltreSerializer

class CapteurViewSet(viewsets.ModelViewSet):
    queryset = Capteur.objects.all()
    serializer_class = CapteurSerializer

def dashboard(request):
    filtres = Filtre.objects.all()
    capteurs = Capteur.objects.all()
    return render(request, 'dashboard.html', {'filtres': filtres, 'capteurs': capteurs})

def page_filtres(request):
    query = request.GET.get('q', '')
    filtres = Filtre.objects.filter(nom__icontains=query) if query else Filtre.objects.all()

    if request.method == 'POST':
        Filtre.objects.create(
            nom=request.POST['nom'],
            type=request.POST['type'],
            date_installation=request.POST['date_installation'],
            localisation=request.POST['localisation'],
            actif='actif' in request.POST
        )
        return redirect('page_filtres')

    return render(request, 'filtres.html', {'filtres': filtres, 'query': query})

def page_capteurs(request):
    query = request.GET.get('q', '')
    if query:
        capteurs = Capteur.objects.filter(type__icontains=query) | Capteur.objects.filter(filtre__nom__icontains=query)
    else:
        capteurs = Capteur.objects.all()

    if request.method == 'POST':
        filtre_id = request.POST.get('filtre')
        filtre = get_object_or_404(Filtre, id=filtre_id)
        Capteur.objects.create(
            filtre=filtre,
            nom=request.POST['nom'],
            type=request.POST['type'],
            valeur=request.POST['valeur']

        )
        return redirect('page_capteurs')

    filtres = Filtre.objects.all()
    return render(request, 'capteurs.html', {'capteurs': capteurs, 'filtres': filtres, 'query': query})


def delete_filtre(request, id):
    filtre = get_object_or_404(Filtre, id=id)
    if request.method == 'POST':
        filtre.delete()
    return redirect('page_filtres')

def delete_capteur(request, id):
    capteur = get_object_or_404(Capteur, id=id)
    if request.method == 'POST':
        capteur.delete()
    return redirect('page_capteurs')

def update_capteur(request, id):
    capteur = get_object_or_404(Capteur, id=id)
    filtres = Filtre.objects.all()

    if request.method == 'POST':
        capteur.nom = request.POST['nom']
        capteur.type = request.POST['type']
        capteur.valeur = request.POST['valeur']
        filtre_id = request.POST['filtre']
        capteur.filtre = get_object_or_404(Filtre, id=filtre_id)
        capteur.save()
        return redirect('page_capteurs')

    return render(request, 'update_capteur.html', {'capteur': capteur, 'filtres': filtres})

def update_filtre(request, id):
    filtre = get_object_or_404(Filtre, id=id)

    if request.method == 'POST':
        filtre.nom = request.POST['nom']
        filtre.type = request.POST['type']
        filtre.date_installation = request.POST['date_installation']
        filtre.localisation = request.POST['localisation']
        filtre.actif = 'actif' in request.POST
        filtre.save()
        return redirect('page_filtres')

    return render(request, 'update_filtre.html', {'filtre': filtre})
