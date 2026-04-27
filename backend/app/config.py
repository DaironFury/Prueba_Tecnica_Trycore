"""Configuración de la aplicación cargada desde variables de entorno.

Los valores se obtienen exclusivamente del entorno del proceso o de un
archivo `.env` local (este último se carga solo si existe, principalmente
para desarrollo local fuera de Docker).

Dentro de un contenedor, el `.env` está excluido intencionalmente (por
`.dockerignore`); compose inyecta las variables mediante `environment:` y
Pydantic las lee directamente desde `os.environ`.

Escribir hostnames como `localhost` está prohibido, ya que la misma imagen
debe ejecutarse en desarrollo local, Docker y CI sin modificaciones.
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación con tipos estrictos.

    `database_url` es el valor más sensible: en Docker debe referenciar
    el nombre del servicio de compose (p.ej. `database`), nunca `localhost`,
    y el driver DEBE ser `postgresql+asyncpg` (el driver síncrono bloquearía
    el event loop).
    """

    app_name: str = Field(default="EVM Dashboard API")
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")

    database_url: str = Field(...)

    # Los orígenes CORS son URLs del lado del NAVEGADOR (p.ej. el usuario
    # abre http://localhost:5173 en el browser). NO son URLs de servicios
    # usadas por el tráfico entre contenedores, por lo que referenciar
    # `localhost` aquí es correcto y no viola la regla de inter-contenedores.
    allowed_origins: str = Field(default="http://localhost")

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("database_url")
    @classmethod
    def _validate_database_url(cls, value: str) -> str:
        """Detecta los errores de configuración más comunes al cargar la config.

        Lanzar aquí produce un mensaje claro en vez de un traceback oscuro
        de SQLAlchemy en el primer request.
        """
        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL debe comenzar con 'postgresql+asyncpg://' "
                "(se requiere driver asíncrono para SQLAlchemy AsyncEngine)."
            )
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retorna una instancia cacheada de Settings.

    Cacheada para que las variables de entorno se lean una sola vez por
    proceso. Usar esta función como dependencia de FastAPI para inyectar
    la configuración.
    """
    return Settings()
