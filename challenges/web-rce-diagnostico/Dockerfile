FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Herramientas del reto. Sin bash ni netcat: la via prevista es una
# reverse shell con PTY usando Python (sockets + pty).
RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Forzar la via Python PTY quitando bash (netcat no se instala).
RUN rm -f /bin/bash /usr/bin/bash

# La flag vive en el sistema de ficheros del contenedor.
RUN printf 'RUBIK{reverse_shell_vault}\n' > /flag.txt

EXPOSE 5000
CMD ["python", "app.py"]
