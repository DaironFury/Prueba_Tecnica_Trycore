"""Repositorio de actividades.

Encapsula todo el acceso a base de datos para actividades. La capa de
servicios llama a este repositorio; los routers no deben hacerlo.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence.orm.activity_orm import ActivityORM


class ActivityRepository:
    """Encapsula todo el acceso a base de datos para actividades."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_project(self, project_id: UUID) -> list[ActivityORM]:
        """Devuelve todas las actividades de un proyecto, ordenadas por creación."""
        result = await self._session.execute(
            select(ActivityORM)
            .where(ActivityORM.project_id == project_id)
            .order_by(ActivityORM.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, activity_id: UUID) -> ActivityORM | None:
        """Devuelve la actividad por su id, o None si no existe."""
        result = await self._session.execute(
            select(ActivityORM).where(ActivityORM.id == activity_id)
        )
        return result.scalar_one_or_none()

    async def create(self, activity: ActivityORM) -> ActivityORM:
        """Persiste una nueva actividad y devuelve la instancia con campos generados por la BD."""
        self._session.add(activity)
        await self._session.commit()
        await self._session.refresh(activity)
        return activity

    async def update(self, activity: ActivityORM) -> ActivityORM:
        """Persiste los cambios de una actividad ya gestionada por la sesión."""
        await self._session.commit()
        await self._session.refresh(activity)
        return activity

    async def delete(self, activity_id: UUID) -> bool:
        """Elimina la actividad y retorna True si existía, False si no se encontró."""
        activity = await self.get_by_id(activity_id)
        if activity is None:
            return False
        await self._session.delete(activity)
        await self._session.commit()
        return True
