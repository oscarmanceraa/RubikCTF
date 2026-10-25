"""Reto Redes: la version del servicio (cabecera Server) revela la flag.

Descubrible con `nmap -sV`.
"""
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

FLAG = os.environ.get("RETO_FLAG", "RUBIK{service_banner}")
PUERTO = int(os.environ.get("PUERTO", "8080"))


class Manejador(BaseHTTPRequestHandler):
    server_version = f"RubikMiniServ/1.0 ({FLAG})"
    sys_version = ""

    def do_GET(self):
        cuerpo = b"<html><body>Servicio interno. Nada que ver aqui.</body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"servicio HTTP en {PUERTO}", flush=True)
    HTTPServer(("0.0.0.0", PUERTO), Manejador).serve_forever()
