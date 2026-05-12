from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,    # POST /api/auth/login/
    TokenRefreshView,       # POST /api/auth/refresh/
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth con JWT
    path('api/auth/login/',   TokenObtainPairView.as_view(),  name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(),     name='token_refresh'),

    # Rutas de cada app (las crearemos en los próximos días)
    path('api/usuarios/',  include('apps.usuarios.urls')),
    path('api/tramites/',  include('apps.tramites.urls')),
]