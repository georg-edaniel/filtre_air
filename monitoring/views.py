from django.shortcuts import render
from django.contrib import messages
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import Filtre, Capteur, Salle
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import FiltreSerializer, CapteurSerializer
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
import random
from datetime import date
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout



def client_salle_all(request):
    salles = Salle.objects.all()
    return render(request, 'client/client_salle_all.html', {'salles': salles})

def creer_salle(request):
    if request.method == 'POST':
        # Récupérer le nom depuis le formulaire
        nom = request.POST.get('nom')
        
        # Créer la salle
        Salle.objects.create(nom=nom)
        
        # Rediriger vers la liste des salles
        return redirect('client_salle_all')  # Adaptez selon le nom de votre URL
    
    # Afficher le formulaire de création
    return render(request, 'creer_salle.html')

def modifier_salle(request, id):
    salle = get_object_or_404(Salle, id=id)
    
    if request.method == 'POST':
        # Récupérer le nouveau nom depuis le formulaire
        nouveau_nom = request.POST.get('nom')
        
        # Mettre à jour la salle
        salle.nom = nouveau_nom
        salle.save()
        
        # Rediriger vers la liste des salles
        return redirect('client_salle_all')  # Adaptez selon le nom de votre URL
    
    # Afficher le formulaire de modification
    return render(request, 'modifier_salle.html', {'salle': salle})

def supprimer_salle(request, id):
    salle = get_object_or_404(Salle, id=id)
    salle.delete()
    return redirect('client_salle_all')
        

class FiltreViewSet(viewsets.ModelViewSet):
    queryset = Filtre.objects.all()
    serializer_class = FiltreSerializer
    permission_classes = [IsAdminUser]

class CapteurViewSet(viewsets.ModelViewSet):
    queryset = Capteur.objects.all()
    serializer_class = CapteurSerializer
    permission_classes = [IsAdminUser]

def dashboard(request):
    salles = Salle.objects.all()
    filtres = Filtre.objects.all()
    capteurs = Capteur.objects.all()
    return render(request, 'dashboard.html', {'filtres': filtres, 'capteurs': capteurs, 'salles': salles})

def page_filtres(request):
    # Seuls les staff peuvent créer/éditer/supprimer via cette vue
    if request.method == 'POST' and not (request.user.is_authenticated and request.user.is_staff):
        return HttpResponseForbidden('Forbidden')
    
    query = request.GET.get('q', '')
    filtres = Filtre.objects.filter(nom__icontains=query) if query else Filtre.objects.all()

    if request.method == 'POST':
        # Vérifier si c'est une création ou une suppression
        if 'delete_id' in request.POST:
            # SUPPRESSION d'un filtre
            try:
                filtre_a_supprimer = Filtre.objects.get(id=request.POST['delete_id'])
                filtre_a_supprimer.delete()
                messages.success(request, "Filtre supprimé avec succès.")
            except Filtre.DoesNotExist:
                messages.error(request, "Le filtre à supprimer n'existe pas.")
            except Exception as e:
                messages.error(request, f"Erreur lors de la suppression : {str(e)}")
                
        else:
            # CRÉATION d'un nouveau filtre
            Filtre.objects.create(
                nom=request.POST['nom'],
                type=request.POST['type'],
                date_installation=request.POST['date_installation'],
                localisation=request.POST['localisation'],
                actif='actif' in request.POST
            )
            messages.success(request, "Filtre créé avec succès.")
            
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


def delete_filtre(request, filtre_id):
    if not (request.user.is_authenticated and request.user.is_staff):
        return HttpResponseForbidden('Forbidden')
    
    try:
        filtre = Filtre.objects.get(id=filtre_id)
        if request.method == 'POST':
            filtre.delete()
            messages.success(request, "Filtre supprimé avec succès.")
            return redirect('page_filtres')
    except Filtre.DoesNotExist:
        messages.error(request, "Le filtre n'existe pas.")
        return redirect('page_filtres')
    
    return HttpResponseNotAllowed(['POST'])

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

@api_view(['POST'])
def ingest_data(request):
    key = request.headers.get('X-ESP32-KEY')
    if key != "change_me":
        return Response({"detail": "Clé API invalide"}, status=403)

    nom = request.data.get("nom")
    type_ = request.data.get("type")
    valeur = request.data.get("valeur")

    if not all([nom, type_, valeur]):
        return Response({"detail": "Champs manquants"}, status=400)

    # ==== Récupération ou création du filtre spécifique ====
    filtre, created = Filtre.objects.get_or_create(
        nom="filtre001",
        defaults={
            "type": "Standard",
            "date_installation": date.today(),
            "localisation": "Salle 1",  # Vous pouvez modifier cette valeur
            "actif": True,
            "vitesse": random.randint(1, 10),
        }
    )

    # ==== Création du capteur associé ====
    capteur = Capteur.objects.create(
        filtre=filtre,
        nom=nom,
        type=type_,
        valeur=valeur
    )

    return Response(
        {
            "detail": "Donnée enregistrée ✅",
            "capteur_id": capteur.id,
            "filtre": filtre.nom,
            "salle": filtre.localisation,
        },
        status=201
    )


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
    try:
        filtre = Filtre.objects.get(id=filtre_id)
        nouvelle_vitesse = request.data['vitesse']
        
        # Mettre à jour en base de données
        filtre.vitesse = nouvelle_vitesse
        filtre.save()
        
        # Envoyer la commande à l'ESP32
        success = envoyer_commande_esp32(filtre, nouvelle_vitesse)
        
        if success:
            return Response({
                "message": f"Vitesse mise à jour à {nouvelle_vitesse}% et envoyée à l'ESP32",
                "success": True
            })
        else:
            return Response({
                "message": f"Vitesse sauvegardée mais ESP32 non accessible",
                "success": False
            })
            
    except Filtre.DoesNotExist:
        return Response({"message": "Filtre non trouvé"}, status=404)
    except Exception as e:
        return Response({"message": f"Erreur: {str(e)}"}, status=500)

def envoyer_commande_esp32(filtre, vitesse):
    """
    Envoie la commande de vitesse à l'ESP32
    """
    try:
        # IP de votre ESP32
        ESP32_IP = "192.168.20.169"  # Assurez-vous que c'est la bonne IP
        
        # Préparer les données - format simplifié
        data = {
            'vitesse': vitesse,
            'filtre_id': filtre.id
        }
        
        print(f"🔄 Envoi commande à ESP32 {ESP32_IP}: {data}")
        
        # Envoyer la commande - CORRECTION: utiliser /api/control au lieu de /controler
        response = requests.post(
            f"http://{ESP32_IP}/api/control",
            json=data,
            timeout=3
        )
        
        print(f"📥 Réponse ESP32: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print(f"✅ Commande envoyée à ESP32: {filtre.nom} à {vitesse}%")
            return True
        else:
            print(f"❌ Erreur ESP32: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectTimeout:
        print(f"❌ Timeout - ESP32 non accessible à {ESP32_IP}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Erreur connexion - Vérifiez l'IP {ESP32_IP}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur requête: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
        return False
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

@login_required(login_url='/login/')
def client_view(request):
    # ton code actuel qui construit le contexte et rend le template client
    context = { 
        'mode': 'salle',
        'salles': Salle.objects.all(),
        'filtres': Filtre.objects.all(),
    }
    return render(request, 'client/client_dashboard.html', context)

@login_required
def deconnexion(request):
    logout(request)
    return redirect('login')  #