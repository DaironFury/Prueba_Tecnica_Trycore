"""Motor asíncrono de SQLAlchemy, fábrica de sesiones y clase base ORM.

El motor se crea a partir de `settings.database_url`, que ya contiene el
host correcto (el nombre del servicio de docker-compose cuando se ejecuta
en Docker, o `localhost` cuando se ejecuta en la máquina host).
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM."""


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia de FastAPI que entrega una sesión transaccional.

    La sesión se revierte automáticamente ante una excepción y se cierra
    al salir del bloque.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
