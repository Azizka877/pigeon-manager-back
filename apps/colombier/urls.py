# apps/colombier/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ColombierConfigViewSet

router = DefaultRouter()
router.register(r'config', ColombierConfigViewSet, basename='colombier-config')

urlpatterns = [
    path('', include(router.urls)),
]