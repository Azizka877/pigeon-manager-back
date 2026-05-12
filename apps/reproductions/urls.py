from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'reproductions', views.ReproductionViewSet, basename='api-reproductions')
router.register(r'', views.ReproductionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
