from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Usuario de RUBIK CTF.

    Se define desde el primer commit porque Django no permite cambiar
    ``AUTH_USER_MODEL`` de forma sencilla una vez creadas las migraciones.

    Nota: los campos ``username``, ``email`` y ``password`` provienen de
    ``AbstractUser`` y se mantienen por requerimiento del framework; en la API
    se exponen como ``usuario`` y ``correo``.
    """

    email = models.EmailField("correo", unique=True)
    nombre_visible = models.CharField("nombre visible", max_length=50, blank=True)

    # Puntuacion total del CTF (se recalcula al resolver retos).
    puntuacion = models.PositiveIntegerField("puntuacion", default=0)

    REQUIRED_FIELDS = ["email"]
    USERNAME_FIELD = "username"

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        ordering = ["-puntuacion", "username"]

    def __str__(self) -> str:
        return self.username
