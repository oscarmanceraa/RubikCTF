# Imagen oficial de Playwright: ya incluye Chromium y sus dependencias.
FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN pip install --no-cache-dir Flask==3.0.3 playwright==1.48.0

COPY app.py .

EXPOSE 5000
CMD ["python", "app.py"]
