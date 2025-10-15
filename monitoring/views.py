from django.shortcuts import render
from django.contrib import messages
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import Filtre, Capteur, Salle
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import FiltreSerializer, CapteurSerializer
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden

class FiltreViewSet(viewsets.ModelViewSet):
    queryset = Filtre.objects.all()
    serializer_class = FiltreSerializer
    permission_classes = [IsAdminUser]

class CapteurViewSet(viewsets.ModelViewSet):
    queryset = Capteur.objects.all()
    serializer_class = CapteurSerializer
    permission_classes = [IsAdminUser]

def dashboard(request):
    filtres = Filtre.objects.all()
    capteurs = Capteur.objects.all()
    return render(request, 'dashboard.html', {'filtres': filtres, 'capteurs': capteurs})

def page_filtres(request):
    # Seuls les staff peuvent créer/éditer/supprimer via cette vue
    if request.method == 'POST' and not (request.user.is_authenticated and request.user.is_staff):
        return HttpResponseForbidden('Forbidden')
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
    # Seuls les staff peuvent créer/éditer/supprimer via cette vue
    if request.method == 'POST' and not (request.user.is_authenticated and request.user.is_staff):
        return HttpResponseForbidden('Forbidden')
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
    if not (request.user.is_authenticated and request.user.is_staff):
        return HttpResponseForbidden('Forbidden')
    filtre = get_object_or_404(Filtre, id=id)
    if request.method == 'POST':
        filtre.delete()
    return redirect('page_filtres')

def delete_capteur(request, id):
    if not (request.user.is_authenticated and request.user.is_staff):
        return HttpResponseForbidden('Forbidden')
    capteur = get_object_or_404(Capteur, id=id)
    if request.method == 'POST':
        capteur.delete()
    return redirect('page_capteurs')

def update_capteur(request, id):
    if not (request.user.is_authenticated and request.user.is_staff):
        return HttpResponseForbidden('Forbidden')
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
    if not (request.user.is_authenticated and request.user.is_staff):
        return HttpResponseForbidden('Forbidden')
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


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Capteur, Filtre

from django.conf import settings

@api_view(['POST'])
def ingest_data(request):
    key = request.headers.get('X-ESP32-KEY')
    if key != "change_me":
        return Response({"detail": "Clé API invalide"}, status=403)

    filtre_id = request.data.get("filtre")
    nom = request.data.get("nom")
    type_ = request.data.get("type")
    valeur = request.data.get("valeur")

    if not all([filtre_id, nom, type_, valeur]):
        return Response({"detail": "Champs manquants"}, status=400)

    try:
        filtre = Filtre.objects.get(id=filtre_id)
    except Filtre.DoesNotExist:
        return Response({"detail": "Filtre introuvable"}, status=404)

    capteur = Capteur.objects.create(
        filtre=filtre,
        nom=nom,
        type=type_,
        valeur=valeur
    )

    return Response({"detail": "Donnée enregistrée", "id": capteur.id}, status=201)


@api_view(['POST'])
def api_create_capteur(request):
    data = request.data
    try:
        filtre = Filtre.objects.get(id=data['filtre'])
        Capteur.objects.create(
            nom=data['nom'],
            type=data['type'],
            valeur=data['valeur'],
            filtre=filtre
        )
        return Response({"message": "Capteur enregistré"}, status=201)
    except Filtre.DoesNotExist:
        return Response({"error": "Filtre introuvable"}, status=400)

@api_view(['POST'])
def modifier_vitesse(request, filtre_id):
    filtre = Filtre.objects.get(id=filtre_id)
    filtre.vitesse = request.data['vitesse']
    filtre.save()
    return Response({"message": "Vitesse mise à jour"})

def client_interface(request):
    # Page principale du client : vue complète (lecture seule)
    salles = Sala = Salle.objects.all()
    capteurs = Capteur.objects.all()
    all_filtres = Filtre.objects.all()
    # mode 'full' rend la vue complète en lecture seule
    return render(request, "client.html", {"mode": "full", "salles": salles, "salles_exists": salles.exists(), "capteurs": capteurs, "all_filtres": all_filtres})


def client_salle(request, salle_id):
    # Vue interactive pour une salle donnée : affiche uniquement les filtres et capteurs de la salle
    salles = Salle.objects.all()
    salle = get_object_or_404(Salle, id=salle_id)
    filtres = Filtre.objects.filter(salle=salle)
    capteurs = Capteur.objects.filter(filtre__in=filtres)
    return render(request, "client.html", {"mode": "salle", "salles": salles, "filtres": filtres, "capteurs": capteurs, "salle_id": str(salle_id), "salles_exists": salles.exists()})


def change_filtre_salle(request, filtre_id):
    """Vue pour changer la salle associée à un filtre depuis l'interface client.
    Attend un POST avec clé 'salle' contenant l'id de la nouvelle salle (ou vide pour None).
    """
    if request.method != 'POST':
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(['POST'])

    filtre = get_object_or_404(Filtre, id=filtre_id)
    salle_id = request.POST.get('salle')
    if salle_id:
        try:
            salle = Salle.objects.get(id=salle_id)
            filtre.salle = salle
        except Salle.DoesNotExist:
            # ignore invalid salle id
            pass
    else:
        filtre.salle = None

    filtre.save()
    # message de confirmation
    if filtre.salle:
        msg = f"Le filtre '{filtre.nom}' a été assigné à la salle '{filtre.salle.nom}'."
    else:
        msg = f"Le filtre '{filtre.nom}' n'est plus assigné à une salle."
    messages.success(request, msg)

    # Si requête AJAX (fetch), renvoyer JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'status': 'ok', 'message': msg, 'salle_id': filtre.salle.id if filtre.salle else None})

    # sinon rediriger vers la page client pour affichage classique
    from django.shortcuts import redirect
    return redirect(f"/client/?salle={filtre.salle.id if filtre.salle else ''}")
