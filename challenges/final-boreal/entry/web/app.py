"""AuroraVault - portal de administracion (contenedor de entrada del reto final)."""
from http.server import BaseHTTPRequestHandler, HTTPServer

PUERTO = 80
RUTA_RESPALDO = "/opt/web/respaldo"

PORTAL = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AuroraVault - Portal de administracion</title>
<style>
  :root{color-scheme:dark}
  body{margin:0;min-height:100vh;color:#e9f0f8;font-family:ui-sans-serif,system-ui,sans-serif;
    background:radial-gradient(900px 500px at 85% -10%, rgba(34,211,238,.14), transparent 60%),#07141c}
  header{display:flex;justify-content:space-between;align-items:center;padding:16px 28px;
    border-bottom:1px solid #1d3d4f;background:rgba(7,20,28,.85)}
  .brand{display:flex;align-items:center;gap:11px;font-weight:700}
  .logo{width:36px;height:36px;border-radius:10px;display:grid;place-items:center;color:#06212a;font-weight:800;
    background:linear-gradient(135deg,#5eead4,#22d3ee)}
  nav a{color:#84a3b3;margin-left:18px;text-decoration:none}
  main{max-width:760px;margin:0 auto;padding:56px 20px}
  h1{font-size:34px;margin:0 0 10px;letter-spacing:-.5px}
  p{color:#84a3b3;line-height:1.6}
  .caja{margin-top:26px;background:#0d2230;border:1px solid #1d3d4f;border-radius:16px;padding:22px}
  code{color:#7cf2a8;font-family:ui-monospace,monospace}
</style></head>
<body>
<header><div class="brand"><div class="logo">AV</div>AuroraVault</div>
<nav><a href="/">Inicio</a><a href="/respaldo/">Respaldos</a><a href="#">Soporte</a></nav></header>
<main>
  <h1>Portal de administracion</h1>
  <p>Consola interna de AuroraVault Storage. Gestion de respaldos y mantenimiento del servidor.</p>
  <div class="caja">
    <p>Servicios: <code>boreal-web</code> · <code>boreal-ssh</code></p>
    <p>Version 3.1 · Acceso restringido al personal autorizado.</p>
  </div>
</main>
</body></html>
"""


class Manejador(BaseHTTPRequestHandler):
    def _enviar(self, codigo, cuerpo, tipo="text/html; charset=utf-8"):
        datos = cuerpo.encode()
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._enviar(200, PORTAL)
        elif self.path == "/robots.txt":
            self._enviar(200, "User-agent: *\nDisallow: /respaldo/\n", "text/plain")
        elif self.path == "/respaldo/":
            self._enviar(
                200,
                "<h1>Respaldos</h1><ul><li><a href='/respaldo/config.bak'>config.bak</a></li></ul>",
            )
        elif self.path == "/respaldo/config.bak":
            try:
                with open(f"{RUTA_RESPALDO}/config.bak", "rb") as archivo:
                    datos = archivo.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(datos)))
                self.end_headers()
                self.wfile.write(datos)
            except FileNotFoundError:
                self._enviar(404, "No encontrado")
        else:
            self._enviar(404, "No encontrado")

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", PUERTO), Manejador).serve_forever()
