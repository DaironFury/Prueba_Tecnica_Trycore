"""Servicio de actividades: casos de uso CRUD para actividades dentro de un proyecto.

Valida que una actividad pertenezca al proyecto solicitado antes de aplicar
cualquier modificación. El cálculo EVM para la respuesta se delega al
calculador de dominio.
"""

from decimal import Decimal
from uuid import UUID

from app.api.exceptions import ActivityNotFoundError, ActivityNotInProjectError, ProjectNotFoundError
from app.api.v1.schemas.activity_schema import ActivityCreateRequest, ActivityDetailResponse, ActivityUpdateRequest
from app.api.v1.schemas.common import EVMIndicatorsSchema
from app.domain.evm_calculator import calculate_activity_indicators
from app.domain.models.activity import ActivityInput
from app.persistence.orm.activity_orm import ActivityORM
from app.persistence.repositories.activity_repository import ActivityRepository
from app.persistence.repositories.project_repository import ProjectRepository


def _build_activity_response(activity: ActivityORM) -> ActivityDetailResponse:
    """Calcula los indicadores EVM de una actividad y los empaqueta en el schema de respuesta."""
    activity_input = ActivityInput(
        bac=float(activity.bac),
        planned_percent=float(activity.planned_percent),
        actual_percent=float(activity.actual_percent),
        actual_cost=float(activity.actual_cost),
    )
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


class ActivityService:
    """Casos de uso: crear, actualizar y eliminar actividades."""

    def __init__(
        self,
        activity_repository: ActivityRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._activities = activity_repository
        self._projects = project_repository

    async def create_activity(
        self, project_id: UUID, data: ActivityCreateRequest
    ) -> ActivityDetailResponse:
        """Crea una actividad en el proyecto dado y devuelve el detalle con indicadores EVM.

        Lanza `ProjectNotFoundError` si el proyecto no existe antes de intentar
        insertar la actividad, para evitar un error de FK de la base de datos.
        """
        project = await self._projects.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)

        activity = ActivityORM(
            project_id=project_id,
            name=data.name,
            bac=Decimal(str(data.bac)),
            planned_percent=Decimal(str(data.planned_percent)),
            actual_percent=Decimal(str(data.actual_percent)),
            actual_cost=Decimal(str(data.actual_cost)),
        )
        saved = await self._activities.create(activity)
        return _build_activity_response(saved)

    async def update_activity(
        self,
        project_id: UUID,
        activity_id: UUID,
        data: ActivityUpdateRequest,
    ) -> ActivityDetailResponse:
        """Actualiza los campos no-None de la actividad y valida que pertenezca al proyecto.

        La validación de pertenencia es un requisito de seguridad: sin ella un
        cliente podría modificar actividades de otros proyectos conociendo solo
        el activity_id.
        """
        project = await self._projects.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)

        activity = await self._activities.get_by_id(activity_id)
        if activity is None:
            raise ActivityNotFoundError(activity_id)
        if activity.project_id != project_id:
            raise ActivityNotInProjectError(activity_id, project_id)

        if data.name is not None:
            activity.name = data.name
        if data.bac is not None:
            activity.bac = Decimal(str(data.bac))
        if data.planned_percent is not None:
            activity.planned_percent = Decimal(str(data.planned_percent))
        if data.actual_percent is not None:
            activity.actual_percent = Decimal(str(data.actual_percent))
        if data.actual_cost is not None:
            activity.actual_cost = Decimal(str(data.actual_cost))

        saved = await self._activities.update(activity)
        return _build_activity_response(saved)

    async def delete_activity(self, project_id: UUID, activity_id: UUID) -> None:
        """Elimina la actividad validando que pertenezca al proyecto.

        Lanza `ActivityNotInProjectError` si el activity_id existe pero
        corresponde a otro proyecto, para distinguir el 404 semántico del 404
        por inexistencia.
        """
        project = await self._projects.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)

        activity = await self._activities.get_by_id(activity_id)
        if activity is None:
            raise ActivityNotFoundError(activity_id)
        if activity.project_id != project_id:
            raise ActivityNotInProjectError(activity_id, project_id)

        await self._activities.delete(activity_id)
