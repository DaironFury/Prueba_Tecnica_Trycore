"""Repositorio de proyectos.

Es la única capa que habla con SQLAlchemy para las entidades `Project`.
Los servicios dependen de esta clase, nunca de `AsyncSession` directamente.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.persistence.orm.project_orm import ProjectORM


class ProjectRepository:
    """Encapsula todo el acceso a base de datos para proyectos."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> list[ProjectORM]:
        """Devuelve todos los proyectos ordenados por fecha de creación descendente."""
        result = await self._session.execute(
            select(ProjectORM).order_by(ProjectORM.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, project_id: UUID) -> ProjectORM | None:
        """Devuelve el proyecto sin cargar actividades, o None si no existe."""
        result = await self._session.execute(
            select(ProjectORM).where(ProjectORM.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_activities(self, project_id: UUID) -> ProjectORM | None:
        """Devuelve el proyecto con sus actividades precargadas, o None si no existe.

        Usar `selectinload` en lugar del lazy="selectin" del ORM garantiza que
        la carga ocurre dentro de esta sesión y evita el error de acceso fuera
        de contexto cuando la sesión ya se cerró.
        """
        result = await self._session.execute(
            select(ProjectORM)
            .options(selectinload(ProjectORM.activities))
            .where(ProjectORM.id == project_id)
        )
        return result.scalar_one_or_none()

    async def create(self, project: ProjectORM) -> ProjectORM:
        """Persiste un nuevo proyecto y devuelve la instancia con los campos generados por la BD."""
        self._session.add(project)
        await self._session.commit()
        await self._session.refresh(project)
        return project

    async def update(self, project: ProjectORM) -> ProjectORM:
        """Persiste los cambios de un proyecto ya gestionado por la sesión."""
        await self._session.commit()
        await self._session.refresh(project)
        return project

    async def delete(self, project_id: UUID) -> bool:
        """Elimina el proyecto y retorna True si existía, False si no se encontró."""
        project = await self.get_by_id(project_id)
        if project is None:
            return False
        await self._session.delete(project)
        await self._session.commit()
        return True
