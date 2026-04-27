"""Fixtures de pytest compartidas para tests unitarios e integración.

Las fixtures `db_session` y `async_client` están disponibles para los tests
de integración. Las fixtures de dominio puro (unit tests) no necesitan ninguna
de estas, ya que no tienen dependencias de BD ni HTTP.
"""

import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db_session
from app.main import app

# La URL de test se lee del entorno para funcionar igual dentro y fuera de Docker.
# Fuera de Docker: DATABASE_URL con `localhost`; dentro del contenedor API: con `database`.
_TEST_DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://evm_user:evm_pass@localhost:5432/evm_db",
)

_test_engine = create_async_engine(_TEST_DB_URL, echo=False, pool_pre_ping=True)
_TestSessionFactory = async_sessionmaker(
    _test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest.fixture(scope="session", autouse=True)
async def _create_tables():
    """Garantiza que las tablas ORM existen antes de los tests de integración.

    `create_all` es idempotente: no sobreescribe tablas que ya existen (útil
    cuando el schema ya fue aplicado por el script de init de docker-compose).
    """
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await _test_engine.dispose()


@pytest.fixture
async def db_session():
    """Provee una sesión con las tablas limpias antes de cada test.

    Usar TRUNCATE + CASCADE en lugar de DROP/CREATE evita el overhead de
    DDL por test y mantiene el aislamiento sin necesidad de savepoints
    (que son más frágiles con asyncpg).
    """
    async with _TestSessionFactory() as session:
        await session.execute(text("TRUNCATE activities, projects CASCADE"))
        await session.commit()
        yield session


@pytest.fixture
async def async_client(db_session: AsyncSession):
    """Cliente HTTP asíncrono que sobreescribe la sesión de BD con la de test.

    El override reemplaza `get_db_session` globalmente durante el test y se
    restaura al salir para no contaminar tests posteriores.
    """

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = _override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
