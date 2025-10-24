from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from monitoring.views import (
    FiltreViewSet,
    CapteurViewSet,
    dashboard,
    page_filtres,
    page_capteurs,
    delete_filtre, 
    delete_capteur,
    update_capteur,
    update_filtre,
    api_create_capteur,
    modifier_vitesse,
    client_interface,
    client_salle,
    change_filtre_salle,
    ingest_data,
    client_salle_all,
    modifier_salle,
    supprimer_salle,
    creer_salle,
    client_view,
    
    
)

router = DefaultRouter()
router.register(r'api/filtres', FiltreViewSet)
router.register(r'api/capteurs', CapteurViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),  # routes API
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/filtres/', page_filtres, name='page_filtres'),
    path('dashboard/capteurs/', page_capteurs, name='page_capteurs'),
    path('dashboard/filtres/delete/<int:id>/', delete_filtre, name='delete_filtre'),
    path('dashboard/capteurs/delete/<int:id>/', delete_capteur, name='delete_capteur'),
    path('dashboard/capteurs/update/<int:id>/', update_capteur, name='update_capteur'),
    path('dashboard/filtres/update/<int:id>/', update_filtre, name='update_filtre'),
    path('api/capteurs/', api_create_capteur),
    path('api/filtre/<int:filtre_id>/vitesse/', modifier_vitesse),
    path('esp32/ingest/', ingest_data),
    path("client/", client_interface, name="client_interface"),
    path('client/salles/<int:salle_id>/', client_salle, name='client_salle'),
    path('client/client_salle_all/', client_salle_all, name='client_salle_all'),
    path('client/filtre/<int:filtre_id>/change_salle/', change_filtre_salle, name='change_filtre_salle'),
   path('modifier_salle/<int:id>/', modifier_salle, name='modifier_salle'),
    path('supprimer_salle/<int:id>/', supprimer_salle, name='supprimer_salle'),
   path('client/creer_salle/', creer_salle, name='creer_salle'),

    # page de login (GET affiche le formulaire, POST connecte)
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    # logout (redirection configurée par LOGOUT_REDIRECT_URL)
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # ta route client 
    path('client/', client_view, name='client_home'),
    # ... autres routes ...
    

]