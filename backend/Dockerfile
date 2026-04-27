# syntax=docker/dockerfile:1.7

# =====================================================================
# Etapa 1 — builder
# Instala las dependencias de Python dentro de un virtualenv aislado.
# Todas las herramientas de compilación (compiladores, cabeceras) viven
# SOLO en esta etapa y nunca llegan a la imagen de runtime.
# =====================================================================
FROM python:3.12.7-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# =====================================================================
# Etapa 2 — runtime
# Imagen mínima: intérprete Python + el venv del builder + código fuente.
# Sin compiladores, sin cachés, sin herramientas de desarrollo.
# Se ejecuta como usuario sin privilegios.
# =====================================================================
FROM python:3.12.7-slim-bookworm AS runtime

LABEL org.opencontainers.image.title="evm-dashboard-api" \
      org.opencontainers.image.description="API backend del EVM Dashboard" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_ENV=production \
    PORT=8000

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --no-create-home --home-dir /app app

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY --chown=app:app . .

USER app

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS "http://localhost:${PORT}/health" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
