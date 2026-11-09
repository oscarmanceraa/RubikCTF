FROM debian:12-slim

ENV DEBIAN_FRONTEND=noninteractive

# openssh + web (python stdlib) + herramientas de enumeracion
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        openssh-server python3 nmap netcat-openbsd iproute2 net-tools procps sudo curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /run/sshd /opt/web/respaldo
COPY web/app.py /opt/web/app.py
COPY web/respaldo/config.bak /opt/web/respaldo/config.bak
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chmod 644 /opt/web/respaldo/config.bak

# Cuenta de bajos privilegios (credenciales filtradas en config.bak)
RUN useradd -m -s /bin/bash mantenimiento \
    && echo 'mantenimiento:Mant3n1m13nto!2024' | chpasswd \
    && printf '%s\n' \
        'Notas de mantenimiento (pendiente de borrar)' \
        '' \
        '- Servidor interno de respaldos: 10.10.10.20' \
        '- Acceso interno: usuario mantenimiento / B0r34l-Int3rno-2024' \
        '- El portal de fuera solo es la fachada, los datos estan dentro.' \
        > /home/mantenimiento/notas.txt \
    && chown -R mantenimiento:mantenimiento /home/mantenimiento

RUN sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config

EXPOSE 22 80
CMD ["/entrypoint.sh"]
