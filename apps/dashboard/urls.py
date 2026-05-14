from django.urls import path
from .views import activites_recentes

urlpatterns = [
    path('activites/', activites_recentes, name='activites_recentes'),
]