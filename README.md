# RubikCTF

Plataforma CTF educativa con progreso representado por un cubo de Rubik.
El participante resuelve retos, obtiene flags, gana puntos y desbloquea
movimientos que el sistema aplica **automaticamente** al cubo.

## Stack

- **Frontend:** React + Vite + Tailwind + Three.js / React Three Fiber
- **Backend:** Python + Django + DRF + SimpleJWT
- **BD:** PostgreSQL
- **Infra:** Docker + Docker Compose + Nginx (Ubuntu Server), Kali Linux para pruebas

## Estado actual

Fases 0-3: estructura del monorepo, `docker-compose.dev.yml`, Django + DRF + JWT,
modelo `Usuario` personalizado, retos, validacion de flags, puntuacion, ranking,
motor del cubo y frontend React con cubo 3D animado (login, registro, panel, retos,
envio de flags, perfil y clasificacion). Todo el codigo esta en espanol.

## Puesta en marcha (dev)

### Opcion A: Docker (recomendada)

Requisitos: Docker + Docker Compose v2.

```bash
cp .env.example .env      # editar valores si es necesario
docker compose -f docker-compose.dev.yml up --build
```

> Si ya habias levantado una version anterior (cambiaron los nombres de apps y
> modelos), borra el volumen de la base de datos:
> `docker compose -f docker-compose.dev.yml down -v`

Servicios:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Admin Django: http://localhost:8000/admin/
- PostgreSQL: localhost:5432

Crear un superusuario para el admin:

```bash
docker compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
```

### Opcion B: nativo (sin Docker)

Backend (requiere Python 3.12+ y PostgreSQL, o SQLite para pruebas):

```bash
cd backend
python -m venv .venv
# Linux/macOS: source .venv/bin/activate   |  Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env        # ajustar POSTGRES_HOST=localhost
# Para probar sin Postgres: export USAR_SQLITE=1
python manage.py migrate
python manage.py runserver
```

Frontend:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

### Rutas del frontend

- `/` inicio
- `/iniciar-sesion`, `/registro`
- `/panel` (protegida)
- `/retos`, `/retos/:slug` (protegidas)
- `/perfil`, `/clasificacion` (protegidas)

### Cubo de Rubik

El cubo se renderiza con Three.js / React Three Fiber en `frontend/src/componentes/CuboRubik.jsx`.
Su estado lo calcula el backend (`/api/cubo/`) a partir de los retos resueltos; el
cliente reproduce la misma logica en `frontend/src/cubo/motor.js` para animar los giros.

- El usuario **no** puede girar las caras: solo puede orbitar la camara para verlo.
- Al resolver un reto, el sistema mueve el cubo automaticamente con una animacion.
- El cubo **empieza desarmado** (se compone con los movimientos de los retos no
  resueltos, en orden canonico) y **queda resuelto al completar todos los retos**,
  sin importar el orden en que se resuelvan.

Colores de cara (tematicos):

| Cara | Color | Categoria |
| ---- | ----- | --------- |
| F | verde | Web |
| R | rojo | Criptografia |
| B | azul | Redes |
| D | amarillo | Forense |
| L | naranja | Reversing |
| U | blanco | OSINT / Esteganografia |

### Probar la API

```bash
# Salud (publico)
curl http://localhost:8000/api/salud/

# Registro
curl -X POST http://localhost:8000/api/autenticacion/registro/ \
  -H "Content-Type: application/json" \
  -d '{"usuario":"neo","correo":"neo@example.com","nombre_visible":"Neo","contrasena":"Sup3rSecret!42"}'

# Login -> devuelve access y refresh
curl -X POST http://localhost:8000/api/autenticacion/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"neo","password":"Sup3rSecret!42"}'

# Perfil (usar el access token)
curl http://localhost:8000/api/autenticacion/perfil/ -H "Authorization: Bearer <ACCESS>"
```

> Nota: el login usa los campos de Django (`username`/`password`); el registro
> expone las claves en espanol (`usuario`/`correo`/`contrasena`).

Crear superusuario para el admin de Django:

```bash
docker compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
```

## Despliegue en Ubuntu Server (produccion)

Arquitectura: **web** (nginx: sirve el frontend compilado y hace de proxy para
`/api`, `/admin` y `/static`) → **backend** (gunicorn + WhiteNoise) → **db** (PostgreSQL).

Archivos usados: `docker-compose.prod.yml`, `frontend/Dockerfile.prod`,
`frontend/nginx.conf`, `.env.prod.example`.

### 1. Crear la VM en VirtualBox

- Tipo Linux, Ubuntu (64-bit). **2 vCPU**, **2-4 GB RAM**, **20 GB** de disco.
- Red: **Adaptador puente (Bridged)** para que tenga una IP en tu LAN (asi Kali la
  alcanza directamente). Alternativa: NAT con redireccion de puerto 80.

### 2. Instalar Ubuntu Server

- ISO de Ubuntu Server 22.04 o 24.04, instalacion minima.
- Marca **Install OpenSSH server**.
- Anota la IP: `ip a` (por ejemplo `192.168.1.50`).

### 3. Instalar Docker

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
# cierra sesion y vuelve a entrar para aplicar el grupo docker
```

### 4. Copiar el proyecto a la VM

Desde tu equipo (git o scp):

```bash
git clone <url-del-repo> RubikCTF
# o desde Kali/Windows:
# scp -r RubikCTF usuario@192.168.1.50:~/
```

### 5. Configurar variables de entorno

```bash
cd ~/RubikCTF
cp .env.prod.example .env
# genera una clave secreta:
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
nano .env
```

Edita en `.env`: `DJANGO_SECRET_KEY`, `POSTGRES_PASSWORD`, y **la IP de la VM** en
`DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` y `CORS_ALLOWED_ORIGINS`
(p. ej. `http://192.168.1.50`).

### 6. Levantar la plataforma

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml logs -f web backend
```

Al arrancar, el backend aplica migraciones y recoge los estaticos automaticamente.

### 7. Crear admin y datos de ejemplo

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
docker compose -f docker-compose.prod.yml exec backend python manage.py sembrar_datos
```

### 8. Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw enable
```

### 9. Acceder

- Desde Kali o cualquier equipo de la LAN: **http://192.168.1.50/**
- Admin: **http://192.168.1.50/admin/**

> HTTPS: para un laboratorio basta HTTP. Si quieres TLS, pon un proxy inverso
> (Caddy/Traefik) con certificado o usa `certbot`, y anade `https://...` a
> `CSRF_TRUSTED_ORIGINS` y `CORS_ALLOWED_ORIGINS`.

## Decisiones arquitectonicas

- **Flags:** se almacenan como hash + pepper (nunca en claro ni en el frontend).
- **Reto-Movimiento:** relacion muchos-a-muchos con orden (`MovimientoReto`).
- **Estado del cubo:** se recalcula desde la secuencia de movimientos desbloqueados
  (la BD es la fuente de verdad).

## API

Publicos:

- `GET /api/salud/`
- `GET /api/categorias/`
- `GET /api/clasificacion/`

Requieren JWT (`Authorization: Bearer <access>`):

- `GET /api/retos/` (filtro opcional `?categoria=<slug>`)
- `GET /api/retos/<slug>/`
- `POST /api/retos/<slug>/enviar/` -> `{"flag": "RUBIK{...}"}`
- `GET /api/cubo/`

Las flags **nunca** se devuelven en las respuestas. La validacion ocurre solo en el
backend y un reto solo otorga puntos una vez por usuario.

### Cargar contenido de prueba

Entrar a `/admin/` (crear superusuario primero), y crear:

1. **Categorias** (Web, Criptografia, Redes, Forense, Reversing, OSINT) con su color.
2. **Movimientos**: `R`, `R'`, `R2`, `U`, `U'`, `F`, `F2`, `L`, `D`, `B`...
3. **Retos**: asignar categoria, dificultad, puntos, `flag` en claro (se guarda
   hasheada) y sus movimientos en el inline.

> Nota: el motor del cubo soporta los 18 movimientos estandar
> (`U R F D L B` con sufijos `''`, `'`, `2`).

## Probar el motor del cubo (sin Django)

```bash
py -3 -c "import sys; sys.path.insert(0,'backend'); from apps.retos import cube_engine as ce; print(ce.esta_resuelto(['R','R','R','R']))"
```

