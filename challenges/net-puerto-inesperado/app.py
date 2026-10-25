"""Reto Redes: servicio TCP en un puerto no estandar que revela la flag.

Descubrible con `nmap -p-` y legible al conectar (nc / nmap -sV).
"""
import os
import socket

FLAG = os.environ.get("RETO_FLAG", "RUBIK{hidden_port}")
PUERTO = int(os.environ.get("PUERTO", "9000"))


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind(("0.0.0.0", PUERTO))
        servidor.listen(16)
        print(f"servicio escuchando en {PUERTO}", flush=True)
        while True:
            conexion, _ = servidor.accept()
            with conexion:
                mensaje = (
                    "RUBIK CTF - servicio interno v1.0\r\n"
                    "No deberias haber encontrado este puerto.\r\n"
                    f"Flag: {FLAG}\r\n"
                )
                conexion.sendall(mensaje.encode())
                conexion.close()


if __name__ == "__main__":
    main()
