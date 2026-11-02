"""Reto Web: login vulnerable a SQL Injection (intranet corporativa ficticia).

Aplicacion deliberadamente vulnerable. Debe ejecutarse AISLADA.
La flag vive en la base de datos de este reto.
"""
import os
import sqlite3

from flask import Flask, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("CHALLENGE_SECRET", "reto-sqli-clave-interna")

BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_BD = os.path.join(BASE, "datos.db")
FLAG = os.environ.get("RETO_FLAG", "RUBIK{sql_injection_101}")

ESTILO = """
<style>
  :root{--fondo:#080b18;--panel:#0f1428;--borde:#242c4a;--texto:#e8ecff;
    --muted:#8b95bd;--indigo:#6366f1;--indigo2:#8b8ff9;--cian:#22d3ee;}
  *{box-sizing:border-box}
  body{margin:0;min-height:100vh;color:var(--texto);
    font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;
    background:radial-gradient(900px 500px at 100% 0%, rgba(99,102,241,.18), transparent 55%),
               radial-gradient(700px 500px at 0% 100%, rgba(34,211,238,.10), transparent 55%),
               var(--fondo);}
  a{color:inherit;text-decoration:none}
  .split{display:grid;grid-template-columns:1.05fr .95fr;min-height:100vh}
  @media(max-width:820px){.split{grid-template-columns:1fr}.marca-panel{display:none}}
  .marca-panel{position:relative;padding:52px;display:flex;flex-direction:column;justify-content:space-between;
    background:linear-gradient(160deg,#121a3a,#0a0f22 65%);border-right:1px solid var(--borde);overflow:hidden}
  .marca-panel::after{content:"";position:absolute;inset:0;pointer-events:none;
    background-image:linear-gradient(rgba(139,149,189,.06) 1px,transparent 1px),
                     linear-gradient(90deg,rgba(139,149,189,.06) 1px,transparent 1px);
    background-size:44px 44px;mask-image:radial-gradient(70% 70% at 30% 30%,#000,transparent)}
  .marca{display:flex;align-items:center;gap:12px;position:relative;z-index:1}
  .logo{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;font-weight:800;font-size:20px;
    color:#0a0f22;background:linear-gradient(135deg,var(--indigo2),var(--indigo));
    box-shadow:0 10px 26px rgba(99,102,241,.35)}
  .marca strong{font-size:18px;letter-spacing:.3px}
  .marca span{display:block;font-size:11px;color:var(--muted);letter-spacing:.16em;text-transform:uppercase}
  .marca-panel h2{font-size:38px;line-height:1.1;margin:0 0 16px;position:relative;z-index:1;letter-spacing:-.6px}
  .marca-panel p{color:var(--muted);max-width:360px;line-height:1.6;position:relative;z-index:1}
  .lista{list-style:none;padding:0;margin:26px 0 0;display:grid;gap:12px;position:relative;z-index:1}
  .lista li{display:flex;align-items:center;gap:10px;color:#c3cbef;font-size:14px}
  .punto{width:9px;height:9px;border-radius:50%;background:var(--cian);box-shadow:0 0 12px var(--cian)}
  .pie{color:#5b6488;font-size:12px;position:relative;z-index:1}

  .acceso{display:flex;align-items:center;justify-content:center;padding:40px 22px}
  .caja{width:100%;max-width:380px}
  .caja h1{font-size:26px;margin:0 0 6px;letter-spacing:-.4px}
  .caja .sub{color:var(--muted);margin:0 0 26px;font-size:14px}
  label{display:block;font-size:13px;color:#aab3da;margin:14px 0 6px}
  input{width:100%;padding:11px 13px;border-radius:11px;border:1px solid var(--borde);
    background:#0a0f22;color:var(--texto);outline:none;font-size:14px}
  input:focus{border-color:var(--indigo);box-shadow:0 0 0 3px rgba(99,102,241,.18)}
  button{margin-top:22px;width:100%;padding:12px;border:0;border-radius:11px;cursor:pointer;
    font-weight:700;color:#fff;background:linear-gradient(135deg,var(--indigo2),var(--indigo))}
  .error{margin-top:16px;padding:11px 13px;border-radius:10px;background:#2a1420;
    border:1px solid #5c1f3a;color:#ff9bb8;font-family:ui-monospace,monospace;font-size:12px;word-break:break-word}
  .nota{margin-top:22px;font-size:12px;color:#5b6488;text-align:center}

  .topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 26px;
    border-bottom:1px solid var(--borde);background:rgba(8,11,24,.85);backdrop-filter:blur(8px)}
  .topbar .marca strong{font-size:15px}
  .chip{display:flex;align-items:center;gap:10px;font-size:13px;color:#c3cbef}
  .chip .avatar{width:30px;height:30px;border-radius:50%;display:grid;place-items:center;font-weight:700;
    background:linear-gradient(135deg,var(--indigo2),var(--indigo));color:#fff;font-size:13px}
  .salir{font-size:13px;color:var(--muted)}
  .salir:hover{color:var(--texto)}
  main.panel{max-width:820px;margin:0 auto;padding:48px 22px}
  main.panel h1{font-size:30px;margin:0 0 6px;letter-spacing:-.5px}
  main.panel .sub{color:var(--muted);margin:0 0 28px}
  .documento{background:var(--panel);border:1px solid var(--borde);border-radius:16px;padding:22px;
    box-shadow:0 24px 60px rgba(0,0,0,.35)}
  .documento h2{font-size:15px;margin:0 0 4px}
  .documento .tag{display:inline-block;font-size:10px;letter-spacing:.16em;text-transform:uppercase;
    color:#ffb3c7;background:#3a1424;border:1px solid #64203a;padding:4px 9px;border-radius:999px;margin-bottom:14px}
  .documento p{color:var(--muted);font-size:14px;line-height:1.6;margin:0 0 16px}
  .secreto{padding:16px 18px;border-radius:12px;background:#0a1622;border:1px solid #1f5c46;
    color:#7CF2A8;font-family:ui-monospace,monospace;font-size:15px;word-break:break-word;
    box-shadow:inset 0 0 30px rgba(124,242,168,.06)}
  .sin{padding:16px 18px;border-radius:12px;background:#1b1220;border:1px solid #4a2440;color:#e6b3d6;
    font-size:14px}
</style>
"""

LOGIN = (
    "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width, initial-scale=1'>"
    "<title>Nexora - Portal del empleado</title>" + ESTILO + "</head><body>"
    "<div class='split'>"
    "<aside class='marca-panel'>"
    "<div class='marca'><div class='logo'>N</div>"
    "<div><strong>Nexora</strong><span>Labs</span></div></div>"
    "<div><h2>Tu trabajo,<br>en un solo lugar.</h2>"
    "<p>Accede al portal interno para gestionar proyectos, documentación y equipos.</p>"
    "<ul class='lista'>"
    "<li><span class='punto'></span> Proyectos y tareas</li>"
    "<li><span class='punto'></span> Documentación interna</li>"
    "<li><span class='punto'></span> Directorio de empleados</li>"
    "</ul></div>"
    "<span class='pie'>© 2026 Nexora Labs · Uso interno</span>"
    "</aside>"
    "<main class='acceso'><div class='caja'>"
    "<h1>Acceso al portal</h1>"
    "<p class='sub'>Identifícate con tu cuenta corporativa.</p>"
    "<form method='post' action='/login'>"
    "<label>Usuario</label><input name='usuario' autocomplete='off'>"
    "<label>Contraseña</label><input name='contrasena' type='password'>"
    "<button type='submit'>Entrar</button></form>"
    "{% if error %}<div class='error'>{{ error }}</div>{% endif %}"
    "<p class='nota'>¿Problemas para acceder? Contacta con soporte de TI.</p>"
    "</div></main></div></body></html>"
)

PANEL = (
    "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width, initial-scale=1'>"
    "<title>Nexora - Panel del empleado</title>" + ESTILO + "</head><body>"
    "<header class='topbar'>"
    "<div class='marca'><div class='logo'>N</div>"
    "<div><strong>Nexora</strong><span>Portal del empleado</span></div></div>"
    "<div class='chip'><div class='avatar'>{{ usuario[0]|upper }}</div>"
    "<span>{{ usuario }}</span><a class='salir' href='/logout'>Cerrar sesión</a></div>"
    "</header>"
    "<main class='panel'>"
    "<h1>Bienvenido, {{ usuario }}</h1>"
    "<p class='sub'>Este es tu espacio de trabajo.</p>"
    "<div class='documento'>"
    "<span class='tag'>Confidencial</span>"
    "<h2>Documento restringido</h2>"
    "{% if flag %}"
    "<p>Solo el personal de administración puede ver este contenido. Se ha registrado tu acceso.</p>"
    "<div class='secreto'>{{ flag }}</div>"
    "{% else %}"
    "<div class='sin'>No tienes permisos para ver este documento.</div>"
    "{% endif %}"
    "</div></main></body></html>"
)


def init_db() -> None:
    con = sqlite3.connect(RUTA_BD)
    con.executescript(
        """
        DROP TABLE IF EXISTS usuarios;
        DROP TABLE IF EXISTS secretos;
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY,
            usuario TEXT,
            contrasena TEXT,
            rol TEXT
        );
        CREATE TABLE secretos (
            id INTEGER PRIMARY KEY,
            secreto TEXT
        );
        INSERT INTO usuarios (usuario, contrasena, rol)
            VALUES ('admin', 'S3cr3t-Adm1n-2024', 'admin');
        INSERT INTO usuarios (usuario, contrasena, rol)
            VALUES ('invitado', 'invitado', 'user');
        """
    )
    con.execute("INSERT INTO secretos (secreto) VALUES (?)", (FLAG,))
    con.commit()
    con.close()


@app.get("/")
def index():
    return render_template_string(LOGIN, error=None)


@app.post("/login")
def login():
    usuario = request.form.get("usuario", "")
    contrasena = request.form.get("contrasena", "")

    # VULNERABILIDAD INTENCIONADA: concatenacion directa de la entrada.
    consulta = (
        f"SELECT * FROM usuarios WHERE usuario = '{usuario}' "
        f"AND contrasena = '{contrasena}'"
    )

    con = sqlite3.connect(RUTA_BD)
    con.row_factory = sqlite3.Row
    error = None
    fila = None
    try:
        fila = con.execute(consulta).fetchone()
    except sqlite3.Error as exc:
        error = f"Error SQL: {exc}"
    finally:
        con.close()

    if fila:
        session["usuario"] = fila["usuario"]
        session["rol"] = fila["rol"]
        return redirect(url_for("panel"))

    return render_template_string(LOGIN, error=error or "Usuario o contraseña incorrectos")


@app.get("/panel")
def panel():
    if "usuario" not in session:
        return redirect(url_for("index"))

    flag = None
    if session.get("rol") == "admin":
        con = sqlite3.connect(RUTA_BD)
        con.row_factory = sqlite3.Row
        flag = con.execute("SELECT secreto FROM secretos").fetchone()["secreto"]
        con.close()

    return render_template_string(PANEL, usuario=session["usuario"], flag=flag)


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if not os.path.exists(RUTA_BD):
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
