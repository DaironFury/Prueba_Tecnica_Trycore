"""Router HTTP para los endpoints de proyectos.

Los routers solo contienen parseo de requests, inyección de dependencias y
armado de respuestas. Toda lógica de negocio debe vivir en la capa de servicios.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.common import DataResponse, MessageResponse
from app.api.v1.schemas.project_schema import (
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectIndicatorsResponse,
    ProjectSummaryResponse,
    ProjectUpdateRequest,
)
from app.database import get_db_session
from app.persistence.repositories.activity_repository import ActivityRepository
from app.persistence.repositories.project_repository import ProjectRepository
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Proyectos"])


def _get_service(session: AsyncSession = Depends(get_db_session)) -> ProjectService:
    """Ensambla el árbol de dependencias: session → repositorios → servicio."""
    return ProjectService(
        project_repository=ProjectRepository(session),
        activity_repository=ActivityRepository(session),
    )


@router.get(
    "",
    response_model=DataResponse[list[ProjectSummaryResponse]],
    summary="Listar todos los proyectos",
)
async def list_projects(service: ProjectService = Depends(_get_service)):
    projects = await service.list_projects()
    return DataResponse(data=projects)


@router.post(
    "",
    response_model=DataResponse[ProjectSummaryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo proyecto",
)
async def create_project(
    payload: ProjectCreateRequest,
    service: ProjectService = Depends(_get_service),
):
    project = await service.create_project(payload)
    return DataResponse(data=project)


@router.get(
    "/{project_id}",
    response_model=DataResponse[ProjectDetailResponse],
    summary="Obtener un proyecto con sus actividades e indicadores EVM",
)
async def get_project(
    project_id: UUID,
    service: ProjectService = Depends(_get_service),
):
    project = await service.get_project_with_indicators(project_id)
    return DataResponse(data=project)


@router.put(
    "/{project_id}",
    response_model=DataResponse[ProjectSummaryResponse],
    summary="Actualizar un proyecto existente",
)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdateRequest,
    service: ProjectService = Depends(_get_service),
):
    project = await service.update_project(project_id, payload)
    return DataResponse(data=project)


@router.delete(
    "/{project_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar un proyecto y sus actividades",
)
async def delete_project(
    project_id: UUID,
    service: ProjectService = Depends(_get_service),
):
    await service.delete_project(project_id)
    return MessageResponse(message="Proyecto eliminado correctamente")


@router.get(
    "/{project_id}/indicators",
    response_model=DataResponse[ProjectIndicatorsResponse],
    summary="Obtener solo los indicadores EVM consolidados de un proyecto",
)
async def get_project_indicators(
    project_id: UUID,
    service: ProjectService = Depends(_get_service),
):
    indicators = await service.get_project_indicators(project_id)
    return DataResponse(data=indicators)
