from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from monitoring.views import (
    FiltreViewSet,
    CapteurViewSet,
    dashboard,
    page_filtres,
    page_capteurs,
    delete_filtre, 
    delete_capteur,
    update_capteur,
    update_filtre
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
    path('dashboard/filtres/update/<int:id>/', update_filtre, name='update_filtre')


]