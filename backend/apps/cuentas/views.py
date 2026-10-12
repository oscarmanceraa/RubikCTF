from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SerializadorRegistro, SerializadorUsuario


class VistaSalud(APIView):
    """Endpoint publico para comprobar que el backend responde."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"estado": "ok", "servicio": "rubikctf-backend"})


class VistaRegistro(generics.CreateAPIView):
    """Registro publico de nuevos participantes."""

    serializer_class = SerializadorRegistro
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializador = self.get_serializer(data=request.data)
        serializador.is_valid(raise_exception=True)
        usuario = serializador.save()
        return Response(SerializadorUsuario(usuario).data, status=status.HTTP_201_CREATED)


class VistaPerfil(generics.RetrieveUpdateAPIView):
    """Datos del usuario autenticado."""

    serializer_class = SerializadorUsuario
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
