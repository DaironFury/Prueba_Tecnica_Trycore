"""Servicio de proyectos: orquesta la persistencia y el cálculo EVM.

Los servicios son los dueños de los casos de uso. Traducen entre los DTOs
de persistencia (`ProjectORM`) y los DTOs de dominio (`ActivityInput`,
`EVMIndicators`), invocan el calculador y devuelven datos listos para la
capa API.
"""

from uuid import UUID

from app.api.exceptions import ProjectNotFoundError
from app.api.v1.schemas.project_schema import (
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectIndicatorsResponse,
    ProjectSummaryResponse,
    ProjectUpdateRequest,
)
from app.api.v1.schemas.activity_schema import ActivityDetailResponse
from app.api.v1.schemas.common import EVMIndicatorsSchema
from app.domain.evm_calculator import calculate_activity_indicators, calculate_project_indicators
from app.domain.models.activity import ActivityInput
from app.persistence.orm.activity_orm import ActivityORM
from app.persistence.orm.project_orm import ProjectORM
from app.persistence.repositories.activity_repository import ActivityRepository
from app.persistence.repositories.project_repository import ProjectRepository


def _orm_to_activity_input(activity: ActivityORM) -> ActivityInput:
    """Convierte un ActivityORM en el dataclass de entrada para el calculador EVM.

    La conversión explícita a float es necesaria porque SQLAlchemy retorna
    `Decimal` para columnas `Numeric`, y el calculador opera solo con floats.
    """
    return ActivityInput(
        bac=float(activity.bac),
        planned_percent=float(activity.planned_percent),
        actual_percent=float(activity.actual_percent),
        actual_cost=float(activity.actual_cost),
    )


def _build_activity_response(activity: ActivityORM) -> ActivityDetailResponse:
    """Calcula los indicadores EVM de una actividad y los empaqueta en el schema de respuesta."""
    activity_input = _orm_to_activity_input(activity)
    indicators = calculate_activity_indicators(activity_input)
    return ActivityDetailResponse(
        id=activity.id,
        project_id=activity.project_id,
        name=activity.name,
        bac=float(activity.bac),
        planned_percent=float(activity.planned_percent),
        actual_percent=float(activity.actual_percent),
        actual_cost=float(activity.actual_cost),
        indicators=EVMIndicatorsSchema.model_validate(indicators, from_attributes=True),
        created_at=activity.created_at,
        updated_at=activity.updated_at,
    )


class ProjectService:
    """Casos de uso: listar, obtener, crear, actualizar y eliminar proyectos."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        activity_repository: ActivityRepository,
    ) -> None:
        self._projects = project_repository
        self._activities = activity_repository

    async def list_projects(self) -> list[ProjectSummaryResponse]:
        """Devuelve todos los proyectos con el conteo de actividades."""
        projects = await self._projects.list_all()
        return [
            ProjectSummaryResponse(
                id=p.id,
                name=p.name,
                description=p.description,
                status_date=p.status_date,
                activity_count=len(p.activities),
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in projects
        ]

    async def get_project_with_indicators(self, project_id: UUID) -> ProjectDetailResponse:
        """Devuelve el proyecto con sus actividades y los indicadores EVM calculados.

        Lanza `ProjectNotFoundError` (→ 404) si el proyecto no existe, para
        que el error_handler lo traduzca a una respuesta JSON estructurada.
        """
        project = await self._projects.get_by_id_with_activities(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)

        activity_responses = [_build_activity_response(a) for a in project.activities]

        activity_inputs = [_orm_to_activity_input(a) for a in project.activities]
        project_indicators = calculate_project_indicators(activity_inputs)

        return ProjectDetailResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status_date=project.status_date,
            indicators=EVMIndicatorsSchema.model_validate(project_indicators, from_attributes=True),
            activities=activity_responses,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

    async def get_project_indicators(self, project_id: UUID) -> ProjectIndicatorsResponse:
        """Devuelve solo los indicadores EVM consolidados del proyecto.

        Útil para dashboards que solo necesitan el resumen sin el listado
        completo de actividades.
        """
        project = await self._projects.get_by_id_with_activities(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)

        activity_inputs = [_orm_to_activity_input(a) for a in project.activities]
        project_indicators = calculate_project_indicators(activity_inputs)

        return ProjectIndicatorsResponse(
            project_id=project.id,
            status_date=project.status_date,
            activity_count=len(project.activities),
            indicators=EVMIndicatorsSchema.model_validate(project_indicators, from_attributes=True),
        )

    async def create_project(self, data: ProjectCreateRequest) -> ProjectSummaryResponse:
        """Crea un nuevo proyecto y devuelve el resumen persistido."""
        project = ProjectORM(
            name=data.name,
            description=data.description,
            status_date=data.status_date,
        )
        saved = await self._projects.create(project)
        return ProjectSummaryResponse(
            id=saved.id,
            name=saved.name,
            description=saved.description,
            status_date=saved.status_date,
            activity_count=0,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    async def update_project(
        self, project_id: UUID, data: ProjectUpdateRequest
    ) -> ProjectSummaryResponse:
        """Actualiza los campos proporcionados del proyecto y devuelve el resumen actualizado.

        Solo los campos distintos de None se aplican, lo que permite peticiones
        PATCH semánticas con un verbo PUT formal.
        """
        project = await self._projects.get_by_id_with_activities(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)

        if data.name is not None:
            project.name = data.name
        if data.description is not None:
            project.description = data.description
        if data.status_date is not None:
            project.status_date = data.status_date

        saved = await self._projects.update(project)
        return ProjectSummaryResponse(
            id=saved.id,
            name=saved.name,
            description=saved.description,
            status_date=saved.status_date,
            activity_count=len(saved.activities),
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    async def delete_project(self, project_id: UUID) -> None:
        """Elimina el proyecto y todas sus actividades (CASCADE en BD).

        Lanza `ProjectNotFoundError` si el proyecto no existe para que el
        cliente reciba un 404 en lugar de un 204 silencioso.
        """
        deleted = await self._projects.delete(project_id)
        if not deleted:
            raise ProjectNotFoundError(project_id)
