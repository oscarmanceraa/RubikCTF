from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import VistaPerfil, VistaRegistro, VistaSalud

app_name = "cuentas"

urlpatterns = [
    path("salud/", VistaSalud.as_view(), name="salud"),
    path("autenticacion/registro/", VistaRegistro.as_view(), name="registro"),
    path("autenticacion/token/", TokenObtainPairView.as_view(), name="token"),
    path("autenticacion/token/refrescar/", TokenRefreshView.as_view(), name="token_refrescar"),
    path("autenticacion/perfil/", VistaPerfil.as_view(), name="perfil"),
]
