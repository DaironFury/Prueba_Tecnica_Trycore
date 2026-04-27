"""Esquemas Pydantic para requests y responses relacionados con proyectos."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.schemas.common import EVMIndicatorsSchema


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status_date: date


class ProjectUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status_date: date | None = None


class ProjectSummaryResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    status_date: date
    activity_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    status_date: date
    indicators: EVMIndicatorsSchema
    activities: list["ActivityDetailResponse"]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectIndicatorsResponse(BaseModel):
    project_id: UUID
    status_date: date
    activity_count: int
    indicators: EVMIndicatorsSchema

    model_config = ConfigDict(from_attributes=True)


from app.api.v1.schemas.activity_schema import ActivityDetailResponse  # noqa: E402

ProjectDetailResponse.model_rebuild()
