from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

Usuario = get_user_model()


class SerializadorUsuario(serializers.ModelSerializer):
    usuario = serializers.CharField(source="username", read_only=True)
    correo = serializers.EmailField(source="email", read_only=True)

    class Meta:
        model = Usuario
        fields = ("id", "usuario", "correo", "nombre_visible", "puntuacion")
        read_only_fields = ("id", "puntuacion")


class SerializadorRegistro(serializers.ModelSerializer):
    usuario = serializers.CharField(source="username")
    correo = serializers.EmailField(source="email")
    contrasena = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = Usuario
        fields = ("id", "usuario", "correo", "nombre_visible", "contrasena")

    def create(self, datos):
        contrasena = datos.pop("contrasena")
        usuario = Usuario(**datos)
        usuario.set_password(contrasena)
        usuario.save()
        return usuario
