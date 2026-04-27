"""Router HTTP para los endpoints de actividades (anidados bajo proyectos)."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.activity_schema import (
    ActivityCreateRequest,
    ActivityDetailResponse,
    ActivityUpdateRequest,
)
from app.api.v1.schemas.common import DataResponse, MessageResponse
from app.database import get_db_session
from app.persistence.repositories.activity_repository import ActivityRepository
from app.persistence.repositories.project_repository import ProjectRepository
from app.services.activity_service import ActivityService

router = APIRouter(
    prefix="/projects/{project_id}/activities",
    tags=["Actividades"],
)


def _get_service(session: AsyncSession = Depends(get_db_session)) -> ActivityService:
    """Ensambla el árbol de dependencias: session → repositorios → servicio."""
    return ActivityService(
        activity_repository=ActivityRepository(session),
        project_repository=ProjectRepository(session),
    )


@router.post(
    "",
    response_model=DataResponse[ActivityDetailResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva actividad dentro de un proyecto",
)
async def create_activity(
    project_id: UUID,
    payload: ActivityCreateRequest,
    service: ActivityService = Depends(_get_service),
):
    activity = await service.create_activity(project_id, payload)
    return DataResponse(data=activity)


@router.put(
    "/{activity_id}",
    response_model=DataResponse[ActivityDetailResponse],
    summary="Actualizar una actividad",
)
async def update_activity(
    project_id: UUID,
    activity_id: UUID,
    payload: ActivityUpdateRequest,
    service: ActivityService = Depends(_get_service),
):
    activity = await service.update_activity(project_id, activity_id, payload)
    return DataResponse(data=activity)


@router.delete(
    "/{activity_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar una actividad",
)
async def delete_activity(
    project_id: UUID,
    activity_id: UUID,
    service: ActivityService = Depends(_get_service),
):
    await service.delete_activity(project_id, activity_id)
    return MessageResponse(message="Actividad eliminada correctamente")
