from django.urls import path

from .views import (
    VistaClasificacion,
    VistaDetalleReto,
    VistaEnvioFlag,
    VistaEstadoCubo,
    VistaListaCategorias,
    VistaListaRetos,
    VistaMascotaReto,
)

app_name = "retos"

urlpatterns = [
    path("categorias/", VistaListaCategorias.as_view(), name="lista_categorias"),
    path("retos/", VistaListaRetos.as_view(), name="lista_retos"),
    path("retos/<slug:slug>/", VistaDetalleReto.as_view(), name="detalle_reto"),
    path("retos/<slug:slug>/enviar/", VistaEnvioFlag.as_view(), name="enviar_flag"),
    path("retos/<slug:slug>/mascota/", VistaMascotaReto.as_view(), name="mascota_reto"),
    path("cubo/", VistaEstadoCubo.as_view(), name="estado_cubo"),
    path("clasificacion/", VistaClasificacion.as_view(), name="clasificacion"),
]
