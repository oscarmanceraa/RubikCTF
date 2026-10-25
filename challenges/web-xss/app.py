"""Reto Web: XSS almacenado (libro de visitas por usuario).

Un bot administrador visita periodicamente el libro de visitas de cada usuario
con la flag en su cookie. El participante debe publicar un comentario que
ejecute JavaScript en el navegador del bot y exfiltre la cookie.

El libro se separa por usuario usando la cookie ``rubik_usuario`` que fija la
plataforma. Asi, al cambiar de usuario, el libro empieza limpio.

Aplicacion deliberadamente vulnerable. Debe ejecutarse AISLADA.
"""
import os
import threading
import time

from flask import Flask, redirect, render_template_string, request

app = Flask(__name__)
FLAG = os.environ.get("RETO_FLAG", "RUBIK{stored_xss_101}")

COMENTARIOS = {}
CANDADO = threading.Lock()
USUARIOS_VISTOS = set()

PLANTILLA = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Libro de visitas</title>
  <style>
    :root { color-scheme: dark; }
    * { box-sizing: border-box; }
    body { margin: 0; background: #0f1117; color: #e7e9ee;
           font-family: ui-sans-serif, system-ui, sans-serif; }
    .contenedor { max-width: 640px; margin: 0 auto; padding: 28px 18px; }
    h1 { font-size: 22px; margin: 0 0 4px; }
    .sub { color: #8b93a3; font-size: 13px; margin: 0 0 20px; }
    form { background: #171a23; border: 1px solid #2a2f3d; border-radius: 12px;
           padding: 16px; display: grid; gap: 10px; }
    input, textarea { width: 100%; padding: 9px 11px; border-radius: 8px;
                      border: 1px solid #2a2f3d; background: #0f1117;
                      color: #e7e9ee; outline: none; font-family: inherit; }
    textarea { min-height: 80px; resize: vertical; }
    button { justify-self: start; padding: 9px 16px; border: 0; border-radius: 8px;
             background: #4f7cff; color: white; font-weight: 600; cursor: pointer; }
    .comentarios { margin-top: 22px; display: grid; gap: 12px; }
    .comentario { background: #171a23; border: 1px solid #2a2f3d;
                  border-radius: 12px; padding: 14px; }
    .autor { font-weight: 600; color: #9fb3ff; font-size: 14px; margin-bottom: 6px; }
    .texto { font-size: 14px; color: #d6dae3; white-space: pre-wrap; word-break: break-word; }
  </style>
</head>
<body>
  <div class="contenedor">
    <h1>Libro de visitas</h1>
    <p class="sub">Sesion: {{ usuario }}. Deja un mensaje; un administrador revisa los comentarios.</p>

    <form method="post" action="/comentario">
      <input name="autor" placeholder="Tu nombre" maxlength="40">
      <textarea name="texto" placeholder="Escribe un comentario..." maxlength="2000"></textarea>
      <button type="submit">Publicar</button>
    </form>

    <div class="comentarios">
      {% for c in comentarios %}
        <div class="comentario">
          <div class="autor">{{ c.autor }}</div>
          <div class="texto">{{ c.texto|safe }}</div>
        </div>
      {% endfor %}
    </div>
  </div>
</body>
</html>
"""


def usuario_actual() -> str:
    nombre = (request.cookies.get("rubik_usuario") or "anonimo").strip()[:40] or "anonimo"
    with CANDADO:
        USUARIOS_VISTOS.add(nombre)
    return nombre


@app.get("/")
def index():
    nombre = usuario_actual()
    with CANDADO:
        comentarios = list(COMENTARIOS.get(nombre, []))
    return render_template_string(PLANTILLA, comentarios=comentarios, usuario=nombre)


@app.post("/comentario")
def comentario():
    nombre = usuario_actual()
    autor = (request.form.get("autor") or "anonimo")[:40]
    texto = (request.form.get("texto") or "")[:2000]
    with CANDADO:
        lista = COMENTARIOS.setdefault(nombre, [])
        lista.append({"autor": autor, "texto": texto})
        del lista[:-50]
    return redirect("/")


def bucle_bot() -> None:
    """El bot visita el libro de cada usuario con la flag en su cookie."""
    from playwright.sync_api import sync_playwright

    while True:
        try:
            with sync_playwright() as p:
                navegador = p.chromium.launch(
                    args=["--no-sandbox", "--disable-dev-shm-usage"]
                )
                while True:
                    with CANDADO:
                        usuarios = list(USUARIOS_VISTOS) or ["anonimo"]
                    for nombre in usuarios:
                        try:
                            contexto = navegador.new_context()
                            contexto.add_cookies(
                                [
                                    {
                                        "name": "rubik_usuario",
                                        "value": nombre,
                                        "url": "http://127.0.0.1:5000",
                                    },
                                    {
                                        "name": "admin",
                                        "value": "1",
                                        "url": "http://127.0.0.1:5000",
                                    },
                                    {
                                        "name": "flag",
                                        "value": FLAG,
                                        "url": "http://127.0.0.1:5000",
                                    },
                                ]
                            )
                            pagina = contexto.new_page()
                            pagina.goto("http://127.0.0.1:5000/", timeout=5000)
                            pagina.wait_for_timeout(1500)
                            contexto.close()
                        except Exception:
                            pass
                    time.sleep(10)
        except Exception:
            time.sleep(10)


if __name__ == "__main__":
    threading.Thread(target=bucle_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, threaded=True)
