from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FiltreViewSet, CapteurViewSet

router = DefaultRouter()
router.register(r'filtres', FiltreViewSet)
router.register(r'capteurs', CapteurViewSet)

urlpatterns = [
    path('', include(router.urls)),
]