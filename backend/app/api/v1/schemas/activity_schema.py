"""Esquemas Pydantic para requests y responses relacionados con actividades."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.schemas.common import EVMIndicatorsSchema


class ActivityCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    bac: float = Field(..., ge=0)
    planned_percent: float = Field(..., ge=0, le=100)
    actual_percent: float = Field(..., ge=0, le=100)
    actual_cost: float = Field(..., ge=0)


class ActivityUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    bac: float | None = Field(default=None, ge=0)
    planned_percent: float | None = Field(default=None, ge=0, le=100)
    actual_percent: float | None = Field(default=None, ge=0, le=100)
    actual_cost: float | None = Field(default=None, ge=0)


class ActivityDetailResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    bac: float
    planned_percent: float
    actual_percent: float
    actual_cost: float
    indicators: EVMIndicatorsSchema
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
