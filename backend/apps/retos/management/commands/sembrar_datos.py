"""Comando de datos de prueba: crea categorias, movimientos y retos.

Es idempotente: se puede ejecutar varias veces sin duplicar registros.

    python manage.py sembrar_datos
    python manage.py sembrar_datos --limpiar   # borra retos que no esten aqui

La URL de los servicios de reto se toma de la variable HOST_RETOS
(por defecto http://192.168.56.77).
"""
import os

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.retos.cube_engine import MOVIMIENTOS
from apps.retos.models import Categoria, MovimientoCubo, MovimientoReto, Reto

BASE_RETOS = os.environ.get("HOST_RETOS", "http://192.168.56.77").rstrip("/")
HOST = BASE_RETOS.replace("http://", "").replace("https://", "")

CATEGORIAS = [
    ("Web", "web", "#2ecc71", 1),
    ("Criptografia", "criptografia", "#ff3b3b", 2),
    ("Redes", "redes", "#2f80ed", 3),
    ("Forense", "forense", "#ffd23f", 4),
    ("Reversing", "reversing", "#ff8c1a", 5),
    ("OSINT / Esteganografia", "osint", "#f2f2f2", 6),
]

# (nombre, slug, categoria, dificultad, puntos, flag, [movimientos], descripcion, objetivo)
RETOS = [
    (
        "Acceso al panel",
        "acceso-al-panel",
        "web",
        "facil",
        150,
        "RUBIK{sql_injection_101}",
        ["L"],
        "Un panel de administracion tiene un login vulnerable a SQL Injection. "
        "Encuentra la flag en su base de datos.",
        f"{BASE_RETOS}:8001",
    ),
    (
        "Base64 en capas",
        "base64-en-capas",
        "criptografia",
        "facil",
        100,
        "RUBIK{base64_layers}",
        ["U"],
        "Un mensaje fue codificado varias veces en Base64. Sigue decodificando "
        "hasta leer la flag.",
        f"{BASE_RETOS}/recursos/base64-capas/mensaje.txt",
    ),
    (
        "Credenciales en el PCAP",
        "credenciales-pcap",
        "redes",
        "media",
        400,
        "RUBIK{pcap_basic_auth}",
        ["R2"],
        "Se capturo trafico HTTP de un login. Abre el PCAP con Wireshark, "
        "sigue el flujo y recupera las credenciales (Basic auth).",
        f"{BASE_RETOS}/recursos/credenciales-pcap/captura.pcap",
    ),
    (
        "Puerto inesperado",
        "puerto-inesperado",
        "redes",
        "facil",
        200,
        "RUBIK{hidden_port}",
        ["F2"],
        f"Escanea el host {HOST} con nmap (-p-). Hay un servicio en un puerto "
        "no estandar; lee su banner y encontraras la flag.",
        "",
    ),
    (
        "Banner revelador",
        "banner-revelador",
        "redes",
        "media",
        350,
        "RUBIK{service_banner}",
        ["B'"],
        f"Escanea el host {HOST} con nmap -sV. La version de uno de los "
        "servicios revela la flag.",
        "",
    ),
]


class Command(BaseCommand):
    help = "Crea categorias, movimientos y retos (idempotente)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limpiar",
            action="store_true",
            help="Elimina los retos que no esten definidos en este seed.",
        )

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
        for (
            nombre,
            slug,
            categoria_slug,
            dificultad,
            puntos,
            flag,
            movimientos,
            descripcion,
            objetivo,
        ) in RETOS:
            reto, creado = Reto.objects.get_or_create(
                slug=slug,
                defaults={
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "objetivo": objetivo,
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
            elif reto.objetivo != objetivo:
                reto.objetivo = objetivo
                reto.save(update_fields=["objetivo"])

        if options.get("limpiar"):
            slugs_validos = [reto[1] for reto in RETOS]
            sobrantes = Reto.objects.exclude(slug__in=slugs_validos)
            eliminados = list(sobrantes.values_list("slug", flat=True))
            sobrantes.delete()
            self.stdout.write(
                self.style.WARNING(f"Retos eliminados: {eliminados or 'ninguno'}")
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Retos creados: {creados} (existentes actualizados si hacia falta). "
                f"Total retos: {Reto.objects.count()}"
            )
        )
