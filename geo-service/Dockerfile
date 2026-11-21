
# ---------- builder: instala las dependencias ----------
FROM python:3.12-slim AS builder

WORKDIR /build

# Solo requirements.txt: esta capa se reutiliza (caché) mientras
# no cambien las dependencias
COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- runner: imagen final ----------
FROM python:3.12-slim AS runner

# Variables de entorno.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Usuario sin privilegios
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

# Dependencias ya instaladas en la etapa builder
COPY --from=builder /install /usr/local

# Copia carpeta app y deja como propietario al usuario app
COPY --chown=app:app app/ ./app/

# A partir de USER app, todo lo que se ejecute en la imagen lo hace el usuario app
USER app 

# La aplicacion escucha en el puerto 8000
EXPOSE 8000

# Cada 10 segundos, Docker lanza un comando el contenedor para llamar a /health
# Si falla 5 veces seguidas, el contenedor pasa a unhealthy.
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
  CMD ["python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/health', timeout=2)"]


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]