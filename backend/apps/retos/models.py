from django.conf import settings
from django.db import models

from . import flags as utilidades_flag


def normalizar_respuesta(valor: str) -> str:
    return " ".join((valor or "").strip().lower().split())


class Dificultad(models.TextChoices):
    FACIL = "facil", "Facil"
    MEDIA = "media", "Media"
    DIFICIL = "dificil", "Dificil"
    EXPERTO = "experto", "Experto"


class Categoria(models.Model):
    """Categoria del CTF, asociada a un color del cubo."""

    nombre = models.CharField("nombre", max_length=50, unique=True)
    slug = models.SlugField("slug", max_length=50, unique=True)
    descripcion = models.TextField("descripcion", blank=True)
    color = models.CharField("color (hex)", max_length=7, default="#00ff9f")
    orden = models.PositiveSmallIntegerField("orden", default=0)
    activa = models.BooleanField("activa", default=True)

    class Meta:
        verbose_name = "categoria"
        verbose_name_plural = "categorias"
        ordering = ["orden", "nombre"]

    def __str__(self) -> str:
        return self.nombre


class MovimientoCubo(models.Model):
    """Movimiento del cubo (notacion Singmaster) que un reto puede desbloquear."""

    notacion = models.CharField("notacion", max_length=2, unique=True)
    descripcion = models.CharField("descripcion", max_length=100, blank=True)
    orden = models.PositiveSmallIntegerField("orden", default=0)

    class Meta:
        verbose_name = "movimiento"
        verbose_name_plural = "movimientos"
        ordering = ["orden", "notacion"]

    def __str__(self) -> str:
        return self.notacion


class Reto(models.Model):
    """Reto del CTF."""

    nombre = models.CharField("nombre", max_length=120)
    slug = models.SlugField("slug", max_length=140, unique=True)
    descripcion = models.TextField("descripcion", blank=True)
    objetivo = models.CharField(
        "objetivo (URL o host)", max_length=200, blank=True,
        help_text="Servicio a atacar, p. ej. http://192.168.56.77:8001",
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="retos", verbose_name="categoria"
    )
    dificultad = models.CharField(
        "dificultad", max_length=10, choices=Dificultad.choices, default=Dificultad.FACIL
    )
    puntos = models.PositiveIntegerField("puntos", default=100)

    # La flag NUNCA se guarda en claro; solo su hash con pepper.
    hash_flag = models.CharField("hash de flag", max_length=64, blank=True)

    activo = models.BooleanField("activo", default=True)
    creado_en = models.DateTimeField("creado", auto_now_add=True)
    actualizado_en = models.DateTimeField("actualizado", auto_now=True)

    movimientos = models.ManyToManyField(
        MovimientoCubo,
        through="MovimientoReto",
        related_name="retos",
        verbose_name="movimientos",
        blank=True,
    )

    class Meta:
        verbose_name = "reto"
        verbose_name_plural = "retos"
        ordering = ["categoria__orden", "puntos", "nombre"]

    def __str__(self) -> str:
        return f"[{self.categoria.slug}] {self.nombre}"

    def establecer_flag(self, flag_en_claro: str) -> None:
        self.hash_flag = utilidades_flag.calcular_hash(flag_en_claro)

    def comprobar_flag(self, flag_en_claro: str) -> bool:
        return utilidades_flag.comprobar_flag(flag_en_claro, self.hash_flag)

    @property
    def movimientos_ordenados(self):
        return [
            mr.movimiento
            for mr in self.movimientos_reto.select_related("movimiento").order_by("orden")
        ]


class MovimientoReto(models.Model):
    """Relacion reto -> movimiento, preservando el orden de aplicacion."""

    reto = models.ForeignKey(Reto, on_delete=models.CASCADE, related_name="movimientos_reto")
    movimiento = models.ForeignKey(MovimientoCubo, on_delete=models.PROTECT)
    orden = models.PositiveSmallIntegerField("orden", default=0)

    class Meta:
        verbose_name = "movimiento del reto"
        verbose_name_plural = "movimientos del reto"
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["reto", "orden"], name="orden_unico_movimiento_reto"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.reto.slug}: {self.movimiento.notacion}"


class Intento(models.Model):
    """Registro de cada intento de envio de flag."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="intentos"
    )
    reto = models.ForeignKey(Reto, on_delete=models.CASCADE, related_name="intentos")
    hash_enviado = models.CharField("hash del envio", max_length=64)
    es_correcto = models.BooleanField("correcto", default=False)
    creado_en = models.DateTimeField("fecha", auto_now_add=True)

    class Meta:
        verbose_name = "intento"
        verbose_name_plural = "intentos"
        ordering = ["-creado_en"]
        indexes = [models.Index(fields=["usuario", "reto"])]

    def __str__(self) -> str:
        estado = "OK" if self.es_correcto else "KO"
        return f"{self.usuario} -> {self.reto.slug} ({estado})"


class RetoResuelto(models.Model):
    """Reto resuelto por un usuario (unico por usuario+reto)."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resueltos"
    )
    reto = models.ForeignKey(Reto, on_delete=models.CASCADE, related_name="resueltos_por")
    puntos_otorgados = models.PositiveIntegerField("puntos otorgados", default=0)
    resuelto_en = models.DateTimeField("resuelto", auto_now_add=True)

    class Meta:
        verbose_name = "reto resuelto"
        verbose_name_plural = "retos resueltos"
        ordering = ["-resuelto_en"]
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "reto"], name="reto_unico_por_usuario"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.usuario} resolvio {self.reto.slug}"


class ProgresoCubo(models.Model):
    """Estado del cubo de un usuario (fuente de verdad: secuencia de movimientos)."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progreso_cubo"
    )
    movimientos_aplicados = models.JSONField("movimientos aplicados", default=list, blank=True)
    actualizado_en = models.DateTimeField("actualizado", auto_now=True)

    class Meta:
        verbose_name = "progreso del cubo"
        verbose_name_plural = "progresos del cubo"

    def __str__(self) -> str:
        return f"Cubo de {self.usuario} ({len(self.movimientos_aplicados)} movs)"

    def agregar_movimientos(self, notaciones) -> None:
        self.movimientos_aplicados = list(self.movimientos_aplicados) + list(notaciones)
        self.save(update_fields=["movimientos_aplicados", "actualizado_en"])

    def reconstruir(self) -> None:
        """Recalcula la secuencia a partir de los retos resueltos (orden de resolucion)."""
        resueltos = (
            RetoResuelto.objects.filter(usuario=self.usuario)
            .select_related("reto")
            .order_by("resuelto_en")
        )
        secuencia = []
        for resuelto in resueltos:
            secuencia.extend(m.notacion for m in resuelto.reto.movimientos_ordenados)
        self.movimientos_aplicados = secuencia
        self.save(update_fields=["movimientos_aplicados", "actualizado_en"])


class Pista(models.Model):
    """Pista asociada a un reto."""

    reto = models.ForeignKey(Reto, on_delete=models.CASCADE, related_name="pistas")
    texto = models.TextField("texto")
    coste = models.PositiveIntegerField("coste en puntos", default=0)
    orden = models.PositiveSmallIntegerField("orden", default=0)
    activa = models.BooleanField("activa", default=True)

    class Meta:
        verbose_name = "pista"
        verbose_name_plural = "pistas"
        ordering = ["orden"]

    def __str__(self) -> str:
        return f"Pista {self.orden} de {self.reto.slug}"


class PreguntaMascota(models.Model):
    """Pregunta de la mascota. Puede desbloquear una pista, nunca la flag."""

    texto = models.TextField("pregunta")
    respuesta = models.CharField("respuesta normalizada", max_length=200)
    tema = models.CharField("tema", max_length=50, blank=True)
    pista = models.ForeignKey(
        Pista, on_delete=models.SET_NULL, null=True, blank=True, related_name="preguntas"
    )
    activa = models.BooleanField("activa", default=True)

    class Meta:
        verbose_name = "pregunta de la mascota"
        verbose_name_plural = "preguntas de la mascota"
        ordering = ["tema", "id"]

    def __str__(self) -> str:
        return self.texto[:60]

    def comprobar_respuesta(self, respuesta_usuario: str) -> bool:
        return normalizar_respuesta(respuesta_usuario) == normalizar_respuesta(self.respuesta)


class PistaDesbloqueada(models.Model):
    """Pista desbloqueada por un usuario."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pistas_desbloqueadas"
    )
    pista = models.ForeignKey(Pista, on_delete=models.CASCADE, related_name="desbloqueadas_por")
    desbloqueada_en = models.DateTimeField("desbloqueada", auto_now_add=True)

    class Meta:
        verbose_name = "pista desbloqueada"
        verbose_name_plural = "pistas desbloqueadas"
        constraints = [
            models.UniqueConstraint(fields=["usuario", "pista"], name="pista_unica_por_usuario"),
        ]

    def __str__(self) -> str:
        return f"{self.usuario} -> pista {self.pista_id}"
