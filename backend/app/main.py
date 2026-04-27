"""Punto de entrada de la aplicación FastAPI.

Este módulo conecta configuración, middleware, manejadores de error y
routers. No contiene lógica de negocio.

El contexto `lifespan` verifica la conectividad a la base de datos al
arrancar para que el contenedor falle rápido (y Docker lo reinicie) cuando
`DATABASE_URL` apunta a un host inalcanzable o las credenciales son incorrectas.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.error_handlers import register_error_handlers
from app.api.v1.router import api_v1_router
from app.config import get_settings
from app.database import engine

settings = get_settings()

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Valida dependencias al arrancar y libera el engine al apagar.

    Ejecutar un `SELECT 1` aquí hace que el contenedor salga con código
    no-cero si la base de datos es inalcanzable. Combinado con
    `restart: unless-stopped` en docker-compose, esto da semántica limpia
    de reintentos durante carreras de arranque que escapan al
    `depends_on: service_healthy` (p.ej. fallos DNS transitorios).
    """
    logger.info("Verificando conectividad con la base de datos en %s", _redact(settings.database_url))
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Conexión a la base de datos exitosa")
    except SQLAlchemyError as exc:
        logger.error("Fallo en la conexión a la base de datos al arrancar: %s", exc)
        raise
    yield
    await engine.dispose()
    logger.info("Engine de base de datos liberado")


def _redact(url: str) -> str:
    """Elimina el segmento de contraseña de una URL de SQLAlchemy para logging seguro."""
    if "@" not in url or "://" not in url:
        return url
    scheme, rest = url.split("://", 1)
    creds, host = rest.split("@", 1)
    if ":" in creds:
        user = creds.split(":", 1)[0]
        return f"{scheme}://{user}:***@{host}"
    return url


app = FastAPI(
    title=settings.app_name,
    description="API REST para gestión de proyectos con indicadores de Valor Ganado (EVM).",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", tags=["Salud"])
async def liveness() -> dict[str, str]:
    """Sonda de liveness: ¿está vivo el proceso?

    Usada por el `HEALTHCHECK` de Docker y por los balanceadores de carga
    para saber si enviar tráfico a esta instancia. NO toca la base de datos,
    por lo que es barata y estable.
    """
    return {"status": "ok"}


@app.get("/health/ready", tags=["Salud"])
async def readiness() -> JSONResponse:
    """Sonda de readiness: ¿puede esta instancia atender tráfico ahora mismo?

    Sondea la base de datos. Retorna 503 con cuerpo estructurado cuando la
    BD es inalcanzable, para que los orquestadores (compose, k8s) puedan
    drenar tráfico sin reiniciar el contenedor innecesariamente.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={"status": "no_disponible", "reason": "base_de_datos_inalcanzable"},
        )
    return JSONResponse(status_code=200, content={"status": "listo"})
