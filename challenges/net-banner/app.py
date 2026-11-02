"""Reto Redes: la version del servicio (cabecera Server) revela la flag.

Descubrible con `nmap -sV`.
"""
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

FLAG = os.environ.get("RETO_FLAG", "RUBIK{service_banner}")
PUERTO = int(os.environ.get("PUERTO", "8080"))

PAGINA = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AuroraVault - Consola</title>
<style>
  :root{color-scheme:dark}
  *{box-sizing:border-box}
  body{margin:0;min-height:100vh;display:grid;place-items:center;color:#e9f0f8;
    font-family:ui-sans-serif,system-ui,sans-serif;
    background:radial-gradient(700px 400px at 80% 0%, rgba(45,212,191,.16), transparent 60%),#08131c}
  .caja{width:360px;background:#0e2030;border:1px solid #1e3b4c;border-radius:16px;padding:28px;
    box-shadow:0 24px 60px rgba(0,0,0,.4)}
  .logo{width:40px;height:40px;border-radius:11px;display:grid;place-items:center;font-weight:800;
    color:#06212a;background:linear-gradient(135deg,#5eead4,#22d3ee);margin-bottom:16px}
  h1{font-size:19px;margin:0 0 4px}
  .sub{color:#8fa6b8;font-size:13px;margin:0 0 20px}
  label{display:block;font-size:12px;color:#9fb4c6;margin:12px 0 5px}
  input{width:100%;padding:9px 11px;border-radius:9px;border:1px solid #1e3b4c;background:#08131c;
    color:#e9f0f8;outline:none}
  button{margin-top:18px;width:100%;padding:10px;border:0;border-radius:9px;font-weight:700;
    color:#06212a;background:linear-gradient(135deg,#5eead4,#22d3ee);cursor:pointer}
  .pie{margin-top:18px;font-size:11px;color:#5f7890;text-align:center}
</style></head>
<body><div class="caja">
  <div class="logo">AV</div>
  <h1>AuroraVault</h1>
  <p class="sub">Consola de administración de respaldos</p>
  <label>Usuario</label><input placeholder="admin">
  <label>Contraseña</label><input type="password" placeholder="••••••••">
  <button>Acceder</button>
  <p class="pie">© 2026 AuroraVault Storage · v3.1</p>
</div></body></html>
"""


class Manejador(BaseHTTPRequestHandler):
    server_version = f"AuroraVault/3.1 ({FLAG})"
    sys_version = ""

    def do_GET(self):
        cuerpo = PAGINA.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"servicio HTTP en {PUERTO}", flush=True)
    HTTPServer(("0.0.0.0", PUERTO), Manejador).serve_forever()
