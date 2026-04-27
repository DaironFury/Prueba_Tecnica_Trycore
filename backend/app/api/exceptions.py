"""Excepciones de dominio lanzadas por la capa de servicios.

Estas excepciones son traducidas a respuestas HTTP por los manejadores
registrados en `app.api.error_handlers`. Los routers y servicios las lanzan
directamente; los routers nunca construyen `HTTPException` por su cuenta.
"""

from uuid import UUID


class DomainError(Exception):
    """Clase base para todas las excepciones de nivel de dominio."""

    code: str = "DOMAIN_ERROR"
    http_status: int = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ProjectNotFoundError(DomainError):
    code = "PROJECT_NOT_FOUND"
    http_status = 404

    def __init__(self, project_id: UUID) -> None:
        super().__init__(f"El proyecto con id '{project_id}' no existe")


class ActivityNotFoundError(DomainError):
    code = "ACTIVITY_NOT_FOUND"
    http_status = 404

    def __init__(self, activity_id: UUID) -> None:
        super().__init__(f"La actividad con id '{activity_id}' no existe")


class ActivityNotInProjectError(DomainError):
    code = "ACTIVITY_NOT_IN_PROJECT"
    http_status = 404

    def __init__(self, activity_id: UUID, project_id: UUID) -> None:
        super().__init__(
            f"La actividad '{activity_id}' no pertenece al proyecto '{project_id}'"
        )
