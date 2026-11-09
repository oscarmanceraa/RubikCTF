"""Reto Web: XSS almacenado (red social ficticia, libro por usuario).

Un bot administrador visita periodicamente el muro de cada usuario con la flag
en su cookie. El participante debe publicar algo que ejecute JavaScript en el
navegador del bot y exfiltre la cookie.

El muro se separa por usuario usando la cookie ``rubik_usuario`` que fija la
plataforma. Asi, al cambiar de usuario, el muro empieza limpio.

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
EVENTO_COMENTARIO = threading.Event()

PLANTILLA = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Nébula - Comunidad</title>
  <style>
    :root{--fondo:#0b0918;--panel:#151029;--borde:#2b2350;--texto:#efeaff;
      --muted:#9a90c2;--violeta:#8b5cf6;--violeta2:#a78bfa;--rosa:#ec4899;}
    *{box-sizing:border-box}
    body{margin:0;min-height:100vh;color:var(--texto);
      font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;
      background:radial-gradient(900px 500px at 100% -10%, rgba(139,92,246,.20), transparent 55%),
                 radial-gradient(700px 500px at 0% 100%, rgba(236,72,153,.12), transparent 55%),
                 var(--fondo);}
    a{color:inherit;text-decoration:none}
    .topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;
      padding:14px 26px;border-bottom:1px solid var(--borde);
      background:rgba(11,9,24,.82);backdrop-filter:blur(8px);position:sticky;top:0;z-index:5}
    .marca{display:flex;align-items:center;gap:11px}
    .logo{width:36px;height:36px;border-radius:11px;display:grid;place-items:center;font-weight:800;font-size:18px;
      color:#140f2b;background:linear-gradient(135deg,var(--violeta2),var(--rosa));
      box-shadow:0 8px 22px rgba(236,72,153,.28)}
    .marca strong{font-size:16px;letter-spacing:.2px}
    nav{display:flex;align-items:center;gap:20px;font-size:14px;color:var(--muted)}
    nav a:hover{color:var(--texto)}
    .chip{display:flex;align-items:center;gap:9px;font-size:13px;color:#cfc7ee;
      padding:6px 12px;border-radius:999px;border:1px solid var(--borde);background:var(--panel)}
    .chip .avatar{width:26px;height:26px;border-radius:50%;display:grid;place-items:center;
      font-weight:700;font-size:12px;color:#fff;background:linear-gradient(135deg,var(--violeta2),var(--violeta))}
    main{max-width:680px;margin:0 auto;padding:34px 18px 60px}
    .encabezado{margin-bottom:20px}
    .encabezado h1{font-size:26px;margin:0 0 4px;letter-spacing:-.4px}
    .encabezado p{color:var(--muted);margin:0;font-size:14px}
    .publicar{background:var(--panel);border:1px solid var(--borde);border-radius:16px;padding:16px;
      display:grid;gap:10px;box-shadow:0 20px 50px rgba(0,0,0,.3)}
    .publicar .fila{display:flex;gap:10px;align-items:center}
    .publicar input{flex:1;padding:10px 12px;border-radius:10px;border:1px solid var(--borde);
      background:#0b0918;color:var(--texto);outline:none;font-size:14px}
    textarea{width:100%;min-height:86px;resize:vertical;padding:12px 13px;border-radius:12px;
      border:1px solid var(--borde);background:#0b0918;color:var(--texto);outline:none;
      font-family:inherit;font-size:14px;line-height:1.5}
    input:focus,textarea:focus{border-color:var(--violeta)}
    .acciones{display:flex;justify-content:flex-end}
    button{padding:10px 20px;border:0;border-radius:10px;cursor:pointer;font-weight:700;color:#fff;
      background:linear-gradient(135deg,var(--violeta2),var(--violeta))}
    .muro{margin-top:24px;display:grid;gap:14px}
    .post{background:var(--panel);border:1px solid var(--borde);border-radius:16px;padding:16px;
      box-shadow:0 16px 40px rgba(0,0,0,.22)}
    .post .cab{display:flex;align-items:center;gap:11px;margin-bottom:10px}
    .post .avatar{width:38px;height:38px;border-radius:50%;display:grid;place-items:center;
      font-weight:700;color:#fff;font-size:15px;
      background:linear-gradient(135deg,var(--violeta2),var(--rosa))}
    .post .quien{font-weight:600;font-size:14px}
    .post .cuando{font-size:12px;color:var(--muted)}
    .post .texto{font-size:14px;line-height:1.6;color:#ddd7f5;white-space:pre-wrap;word-break:break-word}
    .vacio{color:var(--muted);text-align:center;padding:30px 0;font-size:14px}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="marca"><div class="logo">N</div><strong>Nébula</strong></div>
    <nav><a href="#">Inicio</a><a href="#">Explorar</a><a href="#">Comunidad</a></nav>
    <div class="chip"><div class="avatar">{{ usuario[0]|upper }}</div>{{ usuario }}</div>
  </header>

  <main>
    <div class="encabezado">
      <h1>Muro de la comunidad</h1>
      <p>Comparte algo con los demás. Un moderador revisa las publicaciones.</p>
    </div>

    <form class="publicar" method="post" action="/comentario">
      <div class="fila"><input name="autor" placeholder="Tu nombre" maxlength="40"></div>
      <textarea name="texto" placeholder="¿Qué quieres compartir?" maxlength="2000"></textarea>
      <div class="acciones"><button type="submit">Publicar</button></div>
    </form>

    <div class="muro">
      {% for c in comentarios %}
        <article class="post">
          <div class="cab">
            <div class="avatar">{{ c.autor[0]|upper }}</div>
            <div><div class="quien">{{ c.autor }}</div><div class="cuando">hace un momento</div></div>
          </div>
          <div class="texto">{{ c.texto|safe }}</div>
        </article>
      {% else %}
        <p class="vacio">Todavía no hay publicaciones. Sé el primero.</p>
      {% endfor %}
    </div>
  </main>
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
    EVENTO_COMENTARIO.set()
    return redirect("/")


def bucle_bot() -> None:
    """El bot visita el muro de cada usuario con la flag en su cookie."""
    from playwright.sync_api import sync_playwright

    while True:
        try:
            with sync_playwright() as p:
                navegador = p.chromium.launch(
                    args=["--no-sandbox", "--disable-dev-shm-usage"]
                )
                while True:
                    EVENTO_COMENTARIO.wait(timeout=60)
                    EVENTO_COMENTARIO.clear()
                    with CANDADO:
                        usuarios = [u for u, lista in COMENTARIOS.items() if lista]
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
                        time.sleep(2)
                    time.sleep(3)
        except Exception:
            time.sleep(10)


if __name__ == "__main__":
    threading.Thread(target=bucle_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, threaded=True)
