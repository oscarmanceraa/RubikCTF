"""Reto Web: SQL Injection en el buscador de un banco (marca ficticia).

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
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Banco Aurora - Consulta de clientes</title>
  <style>
    :root{
      --fondo:#081424; --panel:#0e2136; --borde:#1e3b5c; --texto:#e9f0f8;
      --muted:#8ea6c2; --oro:#e3b96a; --oro2:#f4d79b;
    }
    *{box-sizing:border-box}
    body{margin:0;min-height:100vh;display:flex;flex-direction:column;color:var(--texto);
      font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;
      background:radial-gradient(1100px 520px at 82% -12%, rgba(227,185,106,.13), transparent 60%),
                 radial-gradient(900px 500px at 0% 110%, rgba(30,90,140,.18), transparent 55%),
                 var(--fondo);}
    a{color:inherit;text-decoration:none}
    .topbar{display:flex;align-items:center;justify-content:space-between;gap:18px;
      padding:16px 30px;border-bottom:1px solid var(--borde);
      background:rgba(8,20,36,.82);backdrop-filter:blur(8px);position:sticky;top:0;z-index:5}
    .marca{display:flex;align-items:center;gap:12px}
    .logo{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;
      color:#0b1a2b;font-weight:800;font-size:19px;
      background:linear-gradient(135deg,var(--oro2),#c98f3a);
      box-shadow:0 8px 20px rgba(227,185,106,.28)}
    .marca strong{display:block;font-size:15px}
    .marca span{display:block;font-size:10px;color:var(--muted);letter-spacing:.16em;text-transform:uppercase}
    nav{display:flex;align-items:center;gap:20px;font-size:14px;color:var(--muted)}
    nav a:hover{color:var(--texto)}
    nav .cta{padding:8px 16px;border-radius:999px;font-weight:700;color:#0b1a2b;
      background:linear-gradient(135deg,var(--oro2),#c98f3a)}
    main{flex:1;width:100%;max-width:980px;margin:0 auto;padding:52px 22px}
    .eyebrow{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--oro);margin:0 0 10px}
    h1{font-size:36px;margin:0 0 10px;letter-spacing:-.6px}
    .lead{color:var(--muted);margin:0 0 26px;max-width:580px;line-height:1.55}
    .buscador{display:flex;gap:10px;background:var(--panel);border:1px solid var(--borde);
      padding:10px;border-radius:15px;box-shadow:0 24px 60px rgba(0,0,0,.35)}
    .buscador input{flex:1;background:transparent;border:0;outline:none;color:var(--texto);
      font-size:15px;padding:8px 10px}
    .buscador input::placeholder{color:var(--muted)}
    .buscador button{background:linear-gradient(135deg,var(--oro2),#c98f3a);color:#0b1a2b;
      border:0;border-radius:10px;padding:10px 22px;font-weight:700;cursor:pointer}
    .tarjeta{margin-top:26px;background:var(--panel);border:1px solid var(--borde);
      border-radius:16px;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,.25)}
    .tarjeta header{padding:14px 18px;border-bottom:1px solid var(--borde);
      display:flex;justify-content:space-between;align-items:center;
      font-size:12px;color:var(--muted);letter-spacing:.08em;text-transform:uppercase}
    table{width:100%;border-collapse:collapse;font-size:14px}
    th,td{text-align:left;padding:13px 18px;border-bottom:1px solid var(--borde)}
    th{color:var(--muted);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.08em}
    tbody tr:hover{background:rgba(227,185,106,.05)}
    td.mono{font-family:ui-monospace,"Cascadia Code",monospace;font-size:13px;color:#cfe0f2}
    .error{padding:13px 16px;border-radius:12px;background:#2a1418;border:1px solid #5c1f2b;
      color:#ff9bb0;font-family:ui-monospace,monospace;font-size:12px;word-break:break-word}
    .vacio{padding:26px 18px;color:var(--muted)}
    footer{padding:20px 30px;border-top:1px solid var(--borde);color:var(--muted);
      font-size:12px;text-align:center}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="marca">
      <div class="logo">A</div>
      <div><strong>Banco Aurora</strong><span>Banca digital</span></div>
    </div>
    <nav>
      <a href="#">Particulares</a>
      <a href="#">Empresas</a>
      <a href="#">Ayuda</a>
      <a class="cta" href="#">Área de clientes</a>
    </nav>
  </header>

  <main>
    <p class="eyebrow">Herramienta interna</p>
    <h1>Consulta de clientes</h1>
    <p class="lead">Localiza la ficha de un cliente por su nombre para revisar sus datos de contacto.</p>

    <form class="buscador" method="get" action="/buscar">
      <input name="q" value="{{ q }}" placeholder="Buscar por nombre (p. ej. Luis)">
      <button type="submit">Buscar</button>
    </form>

    {% if error %}
      <div class="tarjeta" style="margin-top:18px"><div style="padding:16px"><div class="error">{{ error }}</div></div></div>
    {% endif %}

    {% if resultados is not none %}
      <div class="tarjeta">
        <header><span>Resultados</span><span>{{ resultados|length }} registro(s)</span></header>
        {% if resultados %}
          <table>
            <thead><tr><th>ID</th><th>Nombre</th><th>Correo</th></tr></thead>
            <tbody>
            {% for fila in resultados %}
              <tr><td class="mono">{{ fila[0] }}</td><td>{{ fila[1] }}</td><td class="mono">{{ fila[2] }}</td></tr>
            {% endfor %}
            </tbody>
          </table>
        {% else %}
          <p class="vacio">Sin resultados. Prueba con otro nombre.</p>
        {% endif %}
      </div>
    {% endif %}
  </main>

  <footer>© 2026 Banco Aurora · Banca digital · Atención al cliente 900 000 000</footer>
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
            ('Ana Torres', 'ana.torres@bancoaurora.local', 12500),
            ('Carlos Ruiz', 'carlos.ruiz@bancoaurora.local', 8300),
            ('Luis Miguel', 'luis.miguel@bancoaurora.local', 45000);
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
