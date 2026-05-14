from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Gestion de Volière API",
        default_version='v1',
        description="API pour la gestion d'une volière à pigeons",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    
    
    
    # Authentification interface
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
     # JWT Authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Api Endpoint
    path('api/pigeons/', include('apps.pigeons.urls')),
    path('api/cages/', include('apps.cages.urls')),
    path('api/couples/', include('apps.couples.urls')),
    path('api/reproductions/', include('apps.reproductions.urls')),
    path('api/sorties/', include('apps.sales.urls')),
     path('api/colombier/', include('apps.colombier.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/', include('apps.dashboard.urls')),
]
