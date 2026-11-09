from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Count, Exists, OuterRef, Value
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

import random

from . import cube_engine
from . import flags as utilidades_flag
from .models import (
    Categoria,
    Intento,
    PistaDesbloqueada,
    PreguntaMascota,
    ProgresoCubo,
    Reto,
    RetoResuelto,
)
from .serializers import (
    SerializadorCategoria,
    SerializadorClasificacion,
    SerializadorEnvioFlag,
    SerializadorRespuestaMascota,
    SerializadorRetoDetalle,
    SerializadorRetoLista,
)

Usuario = get_user_model()


def retos_anotados(usuario):
    """Queryset de retos activos con el campo ``resuelto`` para el usuario."""
    consulta = (
        Reto.objects.filter(activo=True)
        .select_related("categoria")
        .prefetch_related("movimientos_reto__movimiento")
    )
    if usuario and usuario.is_authenticated:
        resueltos = RetoResuelto.objects.filter(usuario=usuario, reto=OuterRef("pk"))
        consulta = consulta.annotate(resuelto=Exists(resueltos))
    else:
        consulta = consulta.annotate(resuelto=Value(False, output_field=BooleanField()))
    return consulta


def _retos_canonicos():
    """Retos activos en orden fijo (categoria, puntos, nombre)."""
    return list(
        Reto.objects.filter(activo=True)
        .prefetch_related("movimientos_reto__movimiento")
        .order_by("categoria__orden", "puntos", "nombre")
    )


def _notaciones_de(reto):
    return [movimiento.notacion for movimiento in reto.movimientos_ordenados]


def secuencia_usuario(usuario):
    """Desorden actual del cubo: movimientos de los retos NO resueltos (orden canonico).

    Asi el cubo empieza desarmado y, al resolver todos los retos, queda resuelto,
    sin importar el orden en que se resuelvan.
    """
    resueltos = set(
        RetoResuelto.objects.filter(usuario=usuario).values_list("reto_id", flat=True)
    )
    secuencia = []
    for reto in _retos_canonicos():
        if reto.id not in resueltos:
            secuencia.extend(_notaciones_de(reto))
    return secuencia


def _delta_al_resolver(usuario, reto):
    """Movimientos a animar para pasar del estado previo al nuevo estado."""
    retos = _retos_canonicos()
    resueltos = set(
        RetoResuelto.objects.filter(usuario=usuario).values_list("reto_id", flat=True)
    )
    posicion = next((i for i, r in enumerate(retos) if r.id == reto.id), None)
    cola = []
    if posicion is not None:
        for siguiente in retos[posicion + 1 :]:
            if siguiente.id not in resueltos:
                cola.extend(_notaciones_de(siguiente))
    bloque = _notaciones_de(reto)
    return cube_engine.invertir_secuencia(cola) + cube_engine.invertir_secuencia(bloque) + cola


class VistaListaCategorias(generics.ListAPIView):
    queryset = Categoria.objects.filter(activa=True)
    serializer_class = SerializadorCategoria
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class VistaListaRetos(generics.ListAPIView):
    serializer_class = SerializadorRetoLista
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        consulta = retos_anotados(self.request.user)
        categoria = self.request.query_params.get("categoria")
        if categoria:
            consulta = consulta.filter(categoria__slug=categoria)
        return consulta


class VistaDetalleReto(generics.RetrieveAPIView):
    serializer_class = SerializadorRetoDetalle
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "slug"

    def get_queryset(self):
        return retos_anotados(self.request.user)


class VistaEnvioFlag(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "envio_flag"

    def post(self, request, slug):
        reto = get_object_or_404(Reto, slug=slug, activo=True)
        serializador = SerializadorEnvioFlag(data=request.data)
        serializador.is_valid(raise_exception=True)
        flag_en_claro = serializador.validated_data["flag"]

        es_correcta = reto.comprobar_flag(flag_en_claro)
        Intento.objects.create(
            usuario=request.user,
            reto=reto,
            hash_enviado=utilidades_flag.calcular_hash(flag_en_claro),
            es_correcto=es_correcta,
        )

        if not es_correcta:
            return Response(
                {"correcto": False, "mensaje": "Flag incorrecta. Sigue intentandolo."},
                status=status.HTTP_200_OK,
            )

        resuelto, creado = RetoResuelto.objects.get_or_create(
            usuario=request.user,
            reto=reto,
            defaults={"puntos_otorgados": reto.puntos},
        )

        progreso, _ = ProgresoCubo.objects.get_or_create(usuario=request.user)

        delta = []
        if creado:
            request.user.puntuacion = (request.user.puntuacion or 0) + reto.puntos
            request.user.save(update_fields=["puntuacion"])
            progreso.agregar_movimientos(_notaciones_de(reto))
            delta = _delta_al_resolver(request.user, reto)

        secuencia = secuencia_usuario(request.user)

        return Response(
            {
                "correcto": True,
                "ya_resuelto": not creado,
                "puntos_otorgados": resuelto.puntos_otorgados if creado else 0,
                "puntuacion_total": request.user.puntuacion,
                "delta": delta,
                "secuencia": secuencia,
                "cubo": cube_engine.estado_desde_movimientos(secuencia),
                "cubo_resuelto": cube_engine.esta_resuelto(secuencia),
                "mensaje": (
                    "Flag correcta. El cubo se ha movido."
                    if creado
                    else "Ya habias resuelto este reto."
                ),
            },
            status=status.HTTP_200_OK,
        )


class VistaEstadoCubo(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        secuencia = secuencia_usuario(request.user)
        return Response(
            {
                "secuencia": secuencia,
                "cubo": cube_engine.estado_desde_movimientos(secuencia),
                "cubo_resuelto": cube_engine.esta_resuelto(secuencia),
            }
        )


def _pregunta_de_reto(reto):
    return (
        PreguntaMascota.objects.filter(activa=True, pista__reto=reto, pista__activa=True)
        .select_related("pista")
        .first()
    )


def _normalizar_espacios(valor: str) -> str:
    return " ".join((valor or "").split())


class VistaMascotaReto(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, slug):
        reto = get_object_or_404(Reto, slug=slug, activo=True)
        pregunta = _pregunta_de_reto(reto)
        if not pregunta:
            return Response({"disponible": False})

        registro = PistaDesbloqueada.objects.filter(
            usuario=request.user, pista=pregunta.pista
        ).first()
        desbloqueada = registro is not None

        datos = {
            "disponible": True,
            "texto": pregunta.texto,
            "tema": pregunta.tema,
            "pista_desbloqueada": desbloqueada,
            "pista": pregunta.pista.texto if desbloqueada else None,
            "minijuego": pregunta.pista.minijuego,
            "completa": bool(registro and registro.completa),
        }

        if desbloqueada and registro.completa:
            datos["pasos"] = pregunta.pista.pasos
            datos["comando"] = pregunta.pista.comando
        elif desbloqueada and pregunta.pista.minijuego == "ordenar" and pregunta.pista.comando:
            tokens = pregunta.pista.comando.split()
            random.shuffle(tokens)
            datos["tokens"] = tokens

        return Response(datos)

    def post(self, request, slug):
        reto = get_object_or_404(Reto, slug=slug, activo=True)
        pregunta = _pregunta_de_reto(reto)
        if not pregunta:
            return Response({"disponible": False}, status=status.HTTP_404_NOT_FOUND)

        serializador = SerializadorRespuestaMascota(data=request.data)
        serializador.is_valid(raise_exception=True)

        if pregunta.comprobar_respuesta(serializador.validated_data["respuesta"]):
            PistaDesbloqueada.objects.get_or_create(
                usuario=request.user, pista=pregunta.pista
            )
            return Response(
                {
                    "correcto": True,
                    "mensaje": "¡Correcto! Aquí tienes una pista.",
                    "pista": pregunta.pista.texto,
                    "minijuego": pregunta.pista.minijuego,
                }
            )

        return Response(
            {"correcto": False, "mensaje": "No es correcto. Inténtalo de nuevo."}
        )


class VistaAyudaReto(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        reto = get_object_or_404(Reto, slug=slug, activo=True)
        pregunta = _pregunta_de_reto(reto)
        if not pregunta:
            return Response({"disponible": False}, status=status.HTTP_404_NOT_FOUND)

        registro = PistaDesbloqueada.objects.filter(
            usuario=request.user, pista=pregunta.pista
        ).first()
        if registro is None:
            return Response(
                {"correcto": False, "mensaje": "Primero responda la pregunta."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if pregunta.pista.minijuego == "ordenar":
            orden = _normalizar_espacios(request.data.get("orden", ""))
            esperado = _normalizar_espacios(pregunta.pista.comando)
            if not esperado or orden != esperado:
                return Response(
                    {
                        "correcto": False,
                        "mensaje": "Casi... revise el orden e inténtelo otra vez.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            if not request.data.get("completado"):
                return Response(
                    {"correcto": False, "mensaje": "Complete el minijuego primero."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        registro.completa = True
        registro.save(update_fields=["completa"])
        return Response(
            {
                "correcto": True,
                "pasos": pregunta.pista.pasos,
                "comando": pregunta.pista.comando,
            }
        )


class VistaClasificacion(generics.ListAPIView):
    serializer_class = SerializadorClasificacion
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return (
            Usuario.objects.filter(is_active=True)
            .annotate(retos_resueltos=Count("resueltos"))
            .order_by("-puntuacion", "username")[:100]
        )
