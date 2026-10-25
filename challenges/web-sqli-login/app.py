"""Reto Web: login vulnerable a SQL Injection.

Aplicacion deliberadamente vulnerable. Debe ejecutarse AISLADA (contenedor propio,
red separada de la plataforma). La flag vive en la base de datos de este reto.
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
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body { margin:0; min-height:100vh; display:grid; place-items:center;
         background:#0f1117; color:#e7e9ee;
         font-family: ui-sans-serif, system-ui, sans-serif; }
  .caja { width:340px; background:#171a23; border:1px solid #2a2f3d;
          border-radius:14px; padding:28px; }
  h1 { font-size:18px; margin:0 0 6px; }
  .sub { font-size:13px; color:#8b93a3; margin:0 0 18px; }
  label { display:block; font-size:13px; color:#9aa3b2; margin:12px 0 5px; }
  input { width:100%; padding:9px 11px; border-radius:9px; border:1px solid #2a2f3d;
          background:#0f1117; color:#e7e9ee; outline:none; }
  input:focus { border-color:#4f7cff; }
  button { margin-top:18px; width:100%; padding:10px; border:0; border-radius:9px;
           background:#4f7cff; color:#fff; font-weight:600; cursor:pointer; }
  .error { margin-top:14px; font-size:12px; color:#ff7a7a; word-break:break-word; }
  .flag { margin-top:18px; padding:12px; border-radius:9px; background:#12251a;
          border:1px solid #1f5c38; color:#7CF2A8; font-family:ui-monospace,monospace;
          font-size:14px; word-break:break-word; }
  .sin { margin-top:18px; font-size:13px; color:#8b93a3; }
  a.salir { display:inline-block; margin-top:16px; font-size:12px; color:#8b93a3; }
</style>
"""

LOGIN = (
    "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
    "<title>Panel de administracion</title>" + ESTILO + "</head><body>"
    "<div class='caja'><h1>Panel de administracion</h1>"
    "<p class='sub'>Acceso restringido al personal.</p>"
    "<form method='post' action='/login'>"
    "<label>Usuario</label><input name='usuario' autocomplete='off'>"
    "<label>Contrasena</label><input name='contrasena' type='password'>"
    "<button type='submit'>Entrar</button></form>"
    "{% if error %}<div class='error'>{{ error }}</div>{% endif %}"
    "</div></body></html>"
)

PANEL = (
    "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
    "<title>Panel</title>" + ESTILO + "</head><body>"
    "<div class='caja'><h1>Bienvenido, {{ usuario }}</h1>"
    "{% if flag %}<p class='sub'>Acceso de administrador concedido.</p>"
    "<div class='flag'>{{ flag }}</div>"
    "{% else %}<p class='sin'>No tienes permisos para ver la flag.</p>{% endif %}"
    "<a class='salir' href='/logout'>Cerrar sesion</a>"
    "</div></body></html>"
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

    return render_template_string(LOGIN, error=error or "Credenciales incorrectas")


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
