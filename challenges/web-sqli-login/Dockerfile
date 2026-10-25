FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Crea la base de datos (con la flag) en la imagen.
RUN python -c "import app; app.init_db()"

EXPOSE 5000

CMD ["python", "app.py"]
