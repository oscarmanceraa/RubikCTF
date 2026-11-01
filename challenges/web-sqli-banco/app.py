"""Reto Web: SQL Injection en el buscador de un banco.

La base de datos tiene una tabla de credenciales. El usuario "luis.miguel"
tiene su contrasena codificada en Base64; al decodificarla se obtiene la flag.

Aplicacion deliberadamente vulnerable. Debe ejecutarse AISLADA.
"""
import base64
import os
import sqlite3

from flask import Flask, redirect, render_template_string, request

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_BD = os.path.join(BASE, "banco.db")
FLAG = os.environ.get("RETO_FLAG", "RUBIK{sqli_banco_luis_miguel}")

PLANTILLA = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Banco Central - Consulta de clientes</title>
  <style>
    :root { color-scheme: dark; }
    * { box-sizing: border-box; }
    body { margin: 0; background: #0f1117; color: #e7e9ee;
           font-family: ui-sans-serif, system-ui, sans-serif; }
    .contenedor { max-width: 760px; margin: 0 auto; padding: 30px 18px; }
    h1 { font-size: 22px; margin: 0 0 4px; }
    .sub { color: #8b93a3; font-size: 13px; margin: 0 0 20px; }
    form { display: flex; gap: 8px; margin-bottom: 20px; }
    input { flex: 1; padding: 10px 12px; border-radius: 9px; border: 1px solid #2a2f3d;
            background: #171a23; color: #e7e9ee; outline: none; }
    button { padding: 10px 18px; border: 0; border-radius: 9px; background: #4f7cff;
             color: white; font-weight: 600; cursor: pointer; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid #2a2f3d; }
    th { color: #8b93a3; font-weight: 600; }
    .error { margin-bottom: 16px; padding: 10px 12px; border-radius: 9px;
             background: #2a1418; border: 1px solid #5c1f2b; color: #ff8b9c;
             font-family: ui-monospace, monospace; font-size: 12px; word-break: break-word; }
    .vacio { color: #8b93a3; font-size: 14px; }
  </style>
</head>
<body>
  <div class="contenedor">
    <h1>Banco Central</h1>
    <p class="sub">Consulta de clientes por nombre.</p>

    <form method="get" action="/buscar">
      <input name="q" value="{{ q }}" placeholder="Buscar por nombre...">
      <button type="submit">Buscar</button>
    </form>

    {% if error %}<div class="error">{{ error }}</div>{% endif %}

    {% if resultados is not none %}
      {% if resultados %}
        <table>
          <thead><tr><th>ID</th><th>Nombre</th><th>Correo</th></tr></thead>
          <tbody>
          {% for fila in resultados %}
            <tr><td>{{ fila[0] }}</td><td>{{ fila[1] }}</td><td>{{ fila[2] }}</td></tr>
          {% endfor %}
          </tbody>
        </table>
      {% else %}
        <p class="vacio">Sin resultados.</p>
      {% endif %}
    {% endif %}
  </div>
</body>
</html>
"""


def init_db() -> None:
    con = sqlite3.connect(RUTA_BD)
    con.executescript(
        """
        DROP TABLE IF EXISTS clientes;
        DROP TABLE IF EXISTS credenciales;
        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            correo TEXT,
            saldo INTEGER
        );
        CREATE TABLE credenciales (
            id INTEGER PRIMARY KEY,
            usuario TEXT,
            password_b64 TEXT
        );
        INSERT INTO clientes (nombre, correo, saldo) VALUES
            ('Ana Torres', 'ana.torres@banco.local', 12500),
            ('Carlos Ruiz', 'carlos.ruiz@banco.local', 8300),
            ('Luis Miguel', 'luis.miguel@banco.local', 45000);
        """
    )
    credenciales = [
        ("ana.torres", base64.b64encode(b"verano2024").decode()),
        ("carlos.ruiz", base64.b64encode(b"Segura!123").decode()),
        ("luis.miguel", base64.b64encode(FLAG.encode()).decode()),
    ]
    con.executemany(
        "INSERT INTO credenciales (usuario, password_b64) VALUES (?, ?)", credenciales
    )
    con.commit()
    con.close()


@app.get("/")
def index():
    return redirect("/buscar")


@app.get("/buscar")
def buscar():
    q = request.args.get("q", "")

    # VULNERABILIDAD INTENCIONADA: concatenacion directa de la entrada.
    consulta = f"SELECT id, nombre, correo FROM clientes WHERE nombre LIKE '%{q}%'"

    con = sqlite3.connect(RUTA_BD)
    error = None
    resultados = []
    try:
        resultados = [list(fila) for fila in con.execute(consulta).fetchall()]
    except sqlite3.Error as exc:
        error = f"Error SQL: {exc}"
    finally:
        con.close()

    return render_template_string(PLANTILLA, resultados=resultados, q=q, error=error)


if not os.path.exists(RUTA_BD):
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
