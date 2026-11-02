"""Reto Web: inyeccion de comandos (blind) -> reverse shell.

La consola de diagnostico de AuroraVault ejecuta ``ping`` con la entrada del
usuario concatenada a una orden de shell. La salida NO se muestra, asi que la
forma prevista de leer la flag es obtener una shell inversa y leer /flag.txt.

Aplicacion deliberadamente vulnerable. Debe ejecutarse AISLADA.
"""
import os
import subprocess

from flask import Flask, render_template_string, request

app = Flask(__name__)

PLANTILLA = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AuroraVault - Diagnostico de red</title>
  <style>
    :root{--fondo:#07141c;--panel:#0d2230;--borde:#1d3d4f;--texto:#e6f2f5;
      --muted:#84a3b3;--cian:#22d3ee;--verde:#5eead4;--rojo:#fb7185;}
    *{box-sizing:border-box}
    body{margin:0;min-height:100vh;display:flex;flex-direction:column;color:var(--texto);
      font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;
      background:radial-gradient(900px 500px at 100% -10%, rgba(34,211,238,.16), transparent 58%),
                 radial-gradient(700px 500px at 0% 110%, rgba(94,234,212,.08), transparent 55%),
                 var(--fondo);}
    a{color:inherit;text-decoration:none}
    .topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;
      padding:15px 28px;border-bottom:1px solid var(--borde);background:rgba(7,20,28,.85);
      backdrop-filter:blur(8px);position:sticky;top:0}
    .marca{display:flex;align-items:center;gap:11px}
    .logo{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;
      font-weight:800;font-size:17px;color:#06212a;
      background:linear-gradient(135deg,var(--verde),var(--cian));
      box-shadow:0 8px 22px rgba(34,211,238,.3)}
    .marca strong{display:block;font-size:15px}
    .marca span{display:block;font-size:10px;color:var(--muted);letter-spacing:.16em;text-transform:uppercase}
    nav{display:flex;gap:20px;font-size:14px;color:var(--muted)}
    nav a:hover{color:var(--texto)}
    main{flex:1;width:100%;max-width:720px;margin:0 auto;padding:48px 20px}
    .eyebrow{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--cian);margin:0 0 8px}
    h1{font-size:32px;margin:0 0 8px;letter-spacing:-.5px}
    .lead{color:var(--muted);margin:0 0 24px;line-height:1.55}
    form{display:flex;gap:10px;background:var(--panel);border:1px solid var(--borde);
      padding:10px;border-radius:14px;box-shadow:0 20px 50px rgba(0,0,0,.3)}
    input{flex:1;background:transparent;border:0;outline:none;color:var(--texto);font-size:15px;
      padding:9px 10px;font-family:ui-monospace,monospace}
    input::placeholder{color:var(--muted)}
    button{background:linear-gradient(135deg,var(--verde),var(--cian));color:#06212a;
      border:0;border-radius:10px;padding:10px 20px;font-weight:700;cursor:pointer}
    .resultado{margin-top:22px;padding:15px 18px;border-radius:12px;font-size:14px;
      border:1px solid var(--borde);background:var(--panel);color:#cfe6ed}
    .resultado.ok{border-color:#1f5c46;color:#7CF2A8;background:#0a1a16}
    .resultado.ko{border-color:#5c1f2b;color:#ff9bb0;background:#1a0c11}
    .nota{margin-top:26px;font-size:12px;color:#5f7d8c;line-height:1.6}
    footer{padding:18px 28px;border-top:1px solid var(--borde);color:#5f7d8c;font-size:12px;text-align:center}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="marca"><div class="logo">AV</div>
      <div><strong>AuroraVault</strong><span>Consola de administración</span></div></div>
    <nav><a href="#">Panel</a><a href="#">Respaldos</a><a href="/">Diagnóstico</a></nav>
  </header>

  <main>
    <p class="eyebrow">Herramienta de red</p>
    <h1>Diagnóstico de conectividad</h1>
    <p class="lead">Comprueba si un host responde. Introduce una IP o un nombre de dominio.</p>

    <form method="post" action="/diagnostico">
      <input name="host" value="{{ host }}" placeholder="192.168.1.1">
      <button type="submit">Ejecutar</button>
    </form>

    {% if resultado %}
      <div class="resultado {{ 'ok' if 'accesible' in resultado else 'ko' }}">{{ resultado }}</div>
    {% endif %}

    <p class="nota">El diagnóstico solo informa de si el host responde. La salida detallada
      del comando no se muestra por motivos de seguridad.</p>
  </main>

  <footer>© 2026 AuroraVault Storage · v3.1 · Soporte interno: ti@auroravault.local</footer>
</body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(PLANTILLA, host="", resultado=None)


@app.post("/diagnostico")
def diagnostico():
    host = request.form.get("host", "")

    # VULNERABILIDAD INTENCIONADA: la entrada se concatena a una orden de shell.
    comando = f"ping -c 1 -W 2 {host}"

    resultado = "Sin respuesta del host."
    try:
        proceso = subprocess.run(
            comando, shell=True, capture_output=True, timeout=8
        )
        if proceso.returncode == 0:
            resultado = "Host accesible."
    except subprocess.TimeoutExpired:
        resultado = "Tiempo de espera agotado."

    return render_template_string(PLANTILLA, host=host, resultado=resultado)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
