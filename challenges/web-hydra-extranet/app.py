"""Reto Web: fuerza bruta de login (Hydra).

La extranet de Nexora usa el usuario "admin" y una contrasena debil incluida en
la lista filtrada publicada en /lista.txt. El formulario no tiene protecciones
de fuerza bruta, de modo que puede atacarse con hydra (http-post-form).

Aplicacion deliberadamente vulnerable. Debe ejecutarse AISLADA.
"""
import os

from flask import Flask, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("CHALLENGE_SECRET", "hydra-extranet-clave")

FLAG = os.environ.get("RETO_FLAG", "RUBIK{hydra_extranet}")
ADMIN_USUARIO = "admin"
ADMIN_CONTRASENA = "sunshine"

PALABRAS = [
    "123456", "password", "12345678", "qwerty", "123456789", "12345", "1234",
    "111111", "1234567", "dragon", "123123", "baseball", "abc123", "football",
    "monkey", "letmein", "shadow", "master", "666666", "qwertyuiop", "123321",
    "mustang", "1234567890", "michael", "superman", "1qaz2wsx", "7777777",
    "121212", "000000", "qazwsx", "123qwe", "killer", "trustno1", "jordan",
    "jennifer", "zxcvbnm", "asdfgh", "hunter", "buster", "soccer", "harley",
    "batman", "andrew", "tigger", "sunshine", "iloveyou", "charlie", "robert",
    "thomas", "hockey", "ranger", "daniel", "starwars", "klaster", "112233",
    "george", "computer", "michelle", "jessica", "pepper", "1111", "zxcvbn",
]

ESTILO = """
<style>
  :root{--fondo:#080b18;--panel:#0f1428;--borde:#242c4a;--texto:#e8ecff;
    --muted:#8b95bd;--indigo:#6366f1;--indigo2:#8b8ff9;--cian:#22d3ee;}
  *{box-sizing:border-box}
  body{margin:0;min-height:100vh;display:flex;flex-direction:column;color:var(--texto);
    font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;
    background:radial-gradient(900px 500px at 100% 0%, rgba(99,102,241,.18), transparent 55%),
               radial-gradient(700px 500px at 0% 100%, rgba(34,211,238,.10), transparent 55%),
               var(--fondo);}
  a{color:inherit;text-decoration:none}
  .topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;
    padding:15px 28px;border-bottom:1px solid var(--borde);background:rgba(8,11,24,.8)}
  .marca{display:flex;align-items:center;gap:11px}
  .logo{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;font-weight:800;
    font-size:18px;color:#0a0f22;background:linear-gradient(135deg,var(--indigo2),var(--indigo));
    box-shadow:0 8px 22px rgba(99,102,241,.35)}
  .marca strong{display:block;font-size:15px}
  .marca span{display:block;font-size:10px;color:var(--muted);letter-spacing:.16em;text-transform:uppercase}
  nav{display:flex;gap:20px;font-size:14px;color:var(--muted)}
  nav a:hover{color:var(--texto)}
  main{flex:1;display:flex;align-items:center;justify-content:center;padding:48px 20px}
  .caja{width:100%;max-width:370px;background:var(--panel);border:1px solid var(--borde);
    border-radius:16px;padding:28px;box-shadow:0 24px 60px rgba(0,0,0,.4)}
  .caja h1{font-size:22px;margin:0 0 6px;letter-spacing:-.4px}
  .caja .sub{color:var(--muted);font-size:13px;margin:0 0 22px}
  label{display:block;font-size:13px;color:#aab3da;margin:13px 0 6px}
  input{width:100%;padding:10px 12px;border-radius:10px;border:1px solid var(--borde);
    background:#0a0f22;color:var(--texto);outline:none;font-size:14px}
  input:focus{border-color:var(--indigo);box-shadow:0 0 0 3px rgba(99,102,241,.18)}
  button{margin-top:20px;width:100%;padding:11px;border:0;border-radius:10px;cursor:pointer;
    font-weight:700;color:#fff;background:linear-gradient(135deg,var(--indigo2),var(--indigo))}
  .error{margin-top:14px;padding:10px 12px;border-radius:9px;background:#2a1420;
    border:1px solid #5c1f3a;color:#ff9bb8;font-size:13px}
  .panel{margin:0 auto;max-width:620px;width:100%}
  .panel h1{font-size:28px;margin:0 0 6px}
  .panel .sub{color:var(--muted);margin:0 0 22px}
  .doc{background:var(--panel);border:1px solid var(--borde);border-radius:16px;padding:22px;
    box-shadow:0 24px 60px rgba(0,0,0,.35)}
  .tag{display:inline-block;font-size:10px;letter-spacing:.16em;text-transform:uppercase;
    color:#a8f0c8;background:#0f2a20;border:1px solid #1f5c46;padding:4px 9px;border-radius:999px;margin-bottom:14px}
  .doc p{color:var(--muted);font-size:14px;line-height:1.6;margin:0 0 14px}
  .secreto{padding:16px 18px;border-radius:12px;background:#0a1622;border:1px solid #1f5c46;
    color:#7CF2A8;font-family:ui-monospace,monospace;font-size:15px;word-break:break-word}
  .aviso{margin-top:16px;font-size:12px;color:var(--muted)}
  .aviso a{color:var(--indigo2)}
  .memo{max-width:640px;margin:0 auto;width:100%}
  .memo h1{font-size:28px;margin:0 0 4px}
  .memo .sub{color:var(--muted);margin:0 0 20px}
  .memo .doc{padding:24px}
  .memo .doc p{font-size:14px;line-height:1.7;color:#c9cff0;margin:0 0 14px}
  .memo .meta{font-size:12px;color:var(--muted);border-bottom:1px solid var(--borde);
    padding-bottom:12px;margin-bottom:16px}
  .memo .doc a{color:var(--indigo2);text-decoration:underline}
</style>
"""

LOGIN = (
    "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width, initial-scale=1'>"
    "<title>Nexora - Extranet</title>" + ESTILO + "</head><body>"
    "<header class='topbar'><div class='marca'><div class='logo'>N</div>"
    "<div><strong>Nexora</strong><span>Extranet</span></div></div>"
    "<nav><a href='#'>Ayuda</a><a href='#'>Soporte</a></nav></header>"
    "<main><div class='caja'>"
    "<h1>Acceso a la extranet</h1>"
    "<p class='sub'>Área reservada al personal de Nexora.</p>"
    "<form method='post' action='/login'>"
    "<label>Usuario</label><input name='usuario' autocomplete='off'>"
    "<label>Contraseña</label><input name='contrasena' type='password'>"
    "<button type='submit'>Entrar</button></form>"
    "{% if error %}<div class='error'>{{ error }}</div>{% endif %}"
    "<p class='aviso'>Incidente Boreal: <a href='/comunicado'>lee el comunicado de Seguridad</a>.</p>"
    "</div></main></body></html>"
)

PANEL = (
    "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width, initial-scale=1'>"
    "<title>Nexora - Panel</title>" + ESTILO + "</head><body>"
    "<header class='topbar'><div class='marca'><div class='logo'>N</div>"
    "<div><strong>Nexora</strong><span>Panel interno</span></div></div>"
    "<nav><a href='/logout'>Cerrar sesión</a></nav></header>"
    "<main><div class='panel'>"
    "<h1>Bienvenido, {{ usuario }}</h1>"
    "<p class='sub'>Acceso concedido al panel de administración.</p>"
    "<div class='doc'><span class='tag'>Confidencial</span>"
    "<p>Solo el personal autorizado puede ver este contenido.</p>"
    "<div class='secreto'>{{ flag }}</div></div>"
    "</div></main></body></html>"
)

COMUNICADO = (
    "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width, initial-scale=1'>"
    "<title>Nexora - Incidente Boreal</title>" + ESTILO + "</head><body>"
    "<header class='topbar'><div class='marca'><div class='logo'>N</div>"
    "<div><strong>Nexora</strong><span>Seguridad</span></div></div>"
    "<nav><a href='/'>Acceso</a></nav></header>"
    "<main><div class='memo'>"
    "<span class='tag'>Comunicado interno</span>"
    "<h1>Incidente Boreal</h1>"
    "<p class='sub'>Dirección de Seguridad · Nexora Labs</p>"
    "<div class='doc panel'>"
    "<p class='meta'>De: Seguridad de la Información · Para: toda la plantilla · Marzo 2026</p>"
    "<p>Durante la campaña de concienciación de marzo detectamos que varios empleados "
    "introdujeron sus credenciales en una web de phishing que imitaba el portal de RRHH. "
    "El atacante recopiló una lista de contraseñas antiguas que todavía circula por el "
    "recurso compartido interno (<a href='/lista.txt'>lista.txt</a>).</p>"
    "<p>La auditoría reveló que la cuenta <b>admin</b> de la extranet nunca se rotó y "
    "sigue usando una de esas contraseñas débiles.</p>"
    "<p>Tu tarea como respuesta a incidentes es verificar el alcance del acceso: entra "
    "en el panel interno y recupera el <b>código de auditoría</b> para cerrar el caso.</p>"
    "</div></div></main></body></html>"
)


@app.get("/")
def index():
    return render_template_string(LOGIN, error=None)


@app.post("/login")
def login():
    usuario = request.form.get("usuario", "")
    contrasena = request.form.get("contrasena", "")
    if usuario == ADMIN_USUARIO and contrasena == ADMIN_CONTRASENA:
        session["admin"] = True
        return render_template_string(PANEL, usuario=ADMIN_USUARIO, flag=FLAG)
    return render_template_string(LOGIN, error="Credenciales incorrectas")


@app.get("/panel")
def panel():
    if not session.get("admin"):
        return redirect(url_for("index"))
    return render_template_string(PANEL, usuario=ADMIN_USUARIO, flag=FLAG)


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.get("/lista.txt")
def lista():
    return app.response_class("\n".join(PALABRAS) + "\n", mimetype="text/plain")


@app.get("/comunicado")
def comunicado():
    return render_template_string(COMUNICADO)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
