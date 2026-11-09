FROM debian:12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server cron sudo procps \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /run/sshd /opt/boreal /root/INCIDENTE_BOREAL /var/backups
COPY backup.sh /opt/boreal/backup.sh
COPY entrypoint.sh /entrypoint.sh
COPY flag.txt /root/INCIDENTE_BOREAL/flag.txt

# Cuenta de mantenimiento (misma clave que la nota del servidor de entrada).
# El script de respaldo lo ejecuta root por cron pero es escribible por
# mantenimiento: ese es el fallo de configuracion a explotar.
RUN chmod +x /entrypoint.sh \
    && chmod 600 /root/INCIDENTE_BOREAL/flag.txt \
    && useradd -m -s /bin/bash mantenimiento \
    && echo 'mantenimiento:B0r34l-Int3rno-2024' | chpasswd \
    && chown mantenimiento:mantenimiento /opt/boreal/backup.sh \
    && chmod 755 /opt/boreal/backup.sh \
    && echo '* * * * * root /opt/boreal/backup.sh' > /etc/cron.d/boreal \
    && chmod 644 /etc/cron.d/boreal \
    && sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22
CMD ["/entrypoint.sh"]
