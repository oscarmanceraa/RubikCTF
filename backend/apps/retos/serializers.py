from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Categoria, MovimientoCubo, Pista, Reto

Usuario = get_user_model()


class SerializadorMovimiento(serializers.ModelSerializer):
    class Meta:
        model = MovimientoCubo
        fields = ("notacion", "descripcion")


class SerializadorCategoria(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ("id", "nombre", "slug", "descripcion", "color", "orden")


class SerializadorRetoLista(serializers.ModelSerializer):
    categoria = SerializadorCategoria(read_only=True)
    etiqueta_dificultad = serializers.CharField(source="get_dificultad_display", read_only=True)
    movimientos = SerializadorMovimiento(source="movimientos_ordenados", many=True, read_only=True)
    resuelto = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Reto
        fields = (
            "id",
            "nombre",
            "slug",
            "categoria",
            "dificultad",
            "etiqueta_dificultad",
            "puntos",
            "resuelto",
            "movimientos",
        )


class SerializadorRetoDetalle(SerializadorRetoLista):
    cantidad_pistas = serializers.SerializerMethodField()

    class Meta(SerializadorRetoLista.Meta):
        fields = SerializadorRetoLista.Meta.fields + (
            "descripcion",
            "objetivo",
            "cantidad_pistas",
        )

    def get_cantidad_pistas(self, obj) -> int:
        return obj.pistas.filter(activa=True).count()


class SerializadorPista(serializers.ModelSerializer):
    desbloqueada = serializers.SerializerMethodField()

    class Meta:
        model = Pista
        fields = ("id", "orden", "coste", "desbloqueada")

    def get_desbloqueada(self, obj) -> bool:
        peticion = self.context.get("request")
        if not peticion or not peticion.user.is_authenticated:
            return False
        return obj.desbloqueadas_por.filter(usuario=peticion.user).exists()


class SerializadorEnvioFlag(serializers.Serializer):
    flag = serializers.CharField(max_length=300, trim_whitespace=True)


class SerializadorClasificacion(serializers.ModelSerializer):
    usuario = serializers.CharField(source="username", read_only=True)
    retos_resueltos = serializers.IntegerField(read_only=True)

    class Meta:
        model = Usuario
        fields = ("id", "usuario", "nombre_visible", "puntuacion", "retos_resueltos")
