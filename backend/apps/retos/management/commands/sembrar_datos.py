"""Comando de datos de prueba: crea categorias, movimientos y retos de ejemplo.

Es idempotente: se puede ejecutar varias veces sin duplicar registros.

    python manage.py sembrar_datos
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.retos.cube_engine import MOVIMIENTOS
from apps.retos.models import Categoria, MovimientoCubo, MovimientoReto, Reto

CATEGORIAS = [
    ("Web", "web", "#2ecc71", 1),
    ("Criptografia", "criptografia", "#ff3b3b", 2),
    ("Redes", "redes", "#2f80ed", 3),
    ("Forense", "forense", "#ffd23f", 4),
    ("Reversing", "reversing", "#ff8c1a", 5),
    ("OSINT / Esteganografia", "osint", "#f2f2f2", 6),
]

# (nombre, slug, categoria_slug, dificultad, puntos, flag, [movimientos])
RETOS = [
    (
        "Credenciales HTTP",
        "credenciales-http",
        "redes",
        "media",
        400,
        "RUBIK{http_credentials}",
        ["R2"],
        "Se capturo trafico HTTP de un login. Encuentra las credenciales enviadas en claro.",
    ),
    (
        "Base64 no es cifrado",
        "base64-no-es-cifrado",
        "criptografia",
        "facil",
        100,
        "RUBIK{base64_is_not_encryption}",
        ["U"],
        "Quien codifica no cifra. Decodifica el mensaje que encontraras en la descripcion del despliegue.",
    ),
    (
        "Cabeceras reveladoras",
        "cabeceras-reveladoras",
        "web",
        "facil",
        150,
        "RUBIK{inspect_headers}",
        ["F"],
        "A veces la informacion sensible viaja en las cabeceras HTTP. Inspecciona las respuestas.",
    ),
]


class Command(BaseCommand):
    help = "Crea categorias, movimientos y retos de ejemplo (idempotente)."

    @transaction.atomic
    def handle(self, *args, **options):
        categorias = {}
        for nombre, slug, color, orden in CATEGORIAS:
            categoria, _ = Categoria.objects.update_or_create(
                slug=slug,
                defaults={"nombre": nombre, "color": color, "orden": orden, "activa": True},
            )
            categorias[slug] = categoria
        self.stdout.write(f"Categorias: {len(categorias)}")

        for notacion in MOVIMIENTOS:
            MovimientoCubo.objects.get_or_create(notacion=notacion)
        self.stdout.write(f"Movimientos: {MovimientoCubo.objects.count()}")

        creados = 0
        for nombre, slug, categoria_slug, dificultad, puntos, flag, movimientos, descripcion in RETOS:
            reto, creado = Reto.objects.get_or_create(
                slug=slug,
                defaults={
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "categoria": categorias[categoria_slug],
                    "dificultad": dificultad,
                    "puntos": puntos,
                    "activo": True,
                },
            )
            if creado:
                reto.establecer_flag(flag)
                reto.save(update_fields=["hash_flag"])
                for orden, notacion in enumerate(movimientos):
                    MovimientoReto.objects.create(
                        reto=reto,
                        movimiento=MovimientoCubo.objects.get(notacion=notacion),
                        orden=orden,
                    )
                creados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Retos creados: {creados} (existentes omitidos). Total retos: {Reto.objects.count()}"
            )
        )
