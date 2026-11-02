FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Herramientas utiles para el reto (ping y reverse shell).
RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping bash netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# La flag vive en el sistema de ficheros del contenedor.
RUN printf 'RUBIK{reverse_shell_vault}\n' > /flag.txt

EXPOSE 5000
CMD ["python", "app.py"]
