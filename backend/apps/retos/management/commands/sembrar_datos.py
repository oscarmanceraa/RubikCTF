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
from apps.retos.models import (
    Categoria,
    MovimientoCubo,
    MovimientoReto,
    Pista,
    PreguntaMascota,
    Reto,
)

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
        f"El servicio esta en {BASE_RETOS}:8001. Encuentra la flag en su base de datos.",
        f"{BASE_RETOS}:8001",
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
        f"El servicio esta en {HOST}:31337. Identificalo con nmap (-sV) y "
        "conectate para leer su banner; encontraras la flag.",
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
        f"El servicio esta en {HOST}:8003. Escanealo con nmap -sV; la version "
        "del servicio revela la flag.",
        f"{BASE_RETOS}:8003",
    ),
    (
        "XSS almacenado",
        "xss-almacenado",
        "web",
        "media",
        400,
        "RUBIK{stored_xss_101}",
        ["R'"],
        f"El servicio esta en {BASE_RETOS}:8004. Es un libro de visitas. "
        "Publica un comentario que robe la cookie del bot administrador.",
        f"{BASE_RETOS}:8004",
    ),
    (
        "Banco central",
        "banco-central",
        "web",
        "media",
        500,
        "RUBIK{sqli_banco_luis_miguel}",
        ["D2"],
        f"El buscador de clientes del banco esta en {BASE_RETOS}:8005 y es "
        "vulnerable a SQL Injection. Hay una tabla de credenciales; el usuario "
        "'luis.miguel' tiene su contrasena en Base64. Decodificala para obtener la flag.",
        f"{BASE_RETOS}:8005",
    ),
    (
        "Diagnostico de red",
        "diagnostico-red",
        "web",
        "dificil",
        700,
        "RUBIK{reverse_shell_vault}",
        ["F"],
        f"La consola de diagnostico de AuroraVault esta en {BASE_RETOS}:8006 y "
        "ejecuta comandos del sistema (la salida no se muestra). El contenedor "
        "no tiene bash ni netcat: consigue una reverse shell con PTY usando "
        "python3 y lee /flag.txt.",
        f"{BASE_RETOS}:8006",
    ),
    (
        "Receta manipulada",
        "receta-manipulada",
        "web",
        "media",
        450,
        "RUBIK{file_upload_doble_extension}",
        ["F'"],
        f"El portal de recetas de Clinica Vita esta en {BASE_RETOS}:8007. Solo "
        "acepta imagenes o PDF y bloquea las extensiones .php... o eso parece. "
        "Consigue ejecutar codigo en el servidor y lee /flag.txt.",
        f"{BASE_RETOS}:8007",
    ),
    (
        "Extranet de Nexora",
        "extranet-hydra",
        "web",
        "media",
        400,
        "RUBIK{hydra_extranet}",
        ["U2"],
        f"Incidente Boreal: una campana de phishing filtro una lista de "
        f"contrasenas antiguas de Nexora. La cuenta 'admin' de la extranet "
        f"({BASE_RETOS}:8009) nunca se roto y usa una de esas contrasenas. "
        "Descarga /lista.txt, fuerza el login con hydra (http-post-form; la "
        "respuesta correcta NO contiene 'incorrectas') y recupera el codigo "
        "de auditoria del panel.",
        f"{BASE_RETOS}:8009",
    ),
]

# slug -> (pregunta, respuesta_normalizada, tema, pista_basica)
MASCOTA = {
    "acceso-al-panel": (
        "¿Qué palabra clave SQL une los resultados de dos consultas?",
        "union",
        "sql",
        "El login concatena tu usuario. Cierra la comilla y comenta el resto con -- para saltarte la contraseña.",
    ),
    "credenciales-pcap": (
        "¿Qué esquema de autenticación HTTP envía usuario:contraseña codificado en Base64?",
        "basic",
        "http",
        "En Wireshark filtra por http y busca la cabecera Authorization; después decodifica el Base64.",
    ),
    "puerto-inesperado": (
        "¿Qué protocolo orientado a conexión devuelve un banner al conectar a un puerto?",
        "tcp",
        "redes",
        "Escanea todos los puertos con nmap y conecta con nc al que no esperabas; el banner trae la flag.",
    ),
    "banner-revelador": (
        "¿Qué opción de nmap (sin el guion) detecta la versión de los servicios?",
        "sv",
        "redes",
        "Usa la detección de versiones; la cabecera del servidor delata la flag.",
    ),
    "xss-almacenado": (
        "¿Qué objeto de JavaScript contiene las cookies de la página?",
        "document.cookie",
        "xss",
        "El comentario se guarda sin escapar. Haz que el bot envíe su cookie al libro.",
    ),
    "banco-central": (
        "¿Qué palabra clave SQL une el resultado de otra consulta al original?",
        "union",
        "sql",
        "El buscador es inyectable. Con UNION puedes leer la tabla de credenciales.",
    ),
    "diagnostico-red": (
        "¿Qué carácter permite encadenar comandos en la shell de Linux? (escríbelo)",
        ";",
        "linux",
        "La entrada se pega a un comando. Encadena el tuyo y ábrete una shell con Python y PTY.",
    ),
    "receta-manipulada": (
        "¿Qué lenguaje se ejecuta en el servidor con extensión .php?",
        "php",
        "web",
        "Solo se valida la última extensión. Prueba una doble extensión como receta.php.jpg.",
    ),
    "extranet-hydra": (
        "¿Qué herramienta de Kali se usa para fuerza bruta de formularios?",
        "hydra",
        "fuerza bruta",
        "Descarga la lista filtrada y prueba con Hydra; la respuesta correcta no contiene 'incorrectas'.",
    ),
}


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
            reto, creado = Reto.objects.update_or_create(
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

        # Mascota: una pregunta por reto y su pista basica.
        for slug, (pregunta, respuesta, tema, texto_pista) in MASCOTA.items():
            reto = Reto.objects.filter(slug=slug).first()
            if not reto:
                continue
            pista, _ = Pista.objects.update_or_create(
                reto=reto,
                orden=0,
                defaults={"texto": texto_pista, "coste": 0, "activa": True},
            )
            PreguntaMascota.objects.update_or_create(
                pista=pista,
                defaults={
                    "texto": pregunta,
                    "respuesta": respuesta,
                    "tema": tema,
                    "activa": True,
                },
            )

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
