"""Sobres de respuesta reutilizables y sub-esquemas compartidos."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class DataResponse(BaseModel, Generic[T]):
    """Sobre estándar para respuestas exitosas con datos."""

    data: T
    message: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Sobre estándar para respuestas exitosas sin datos (por ejemplo, DELETE)."""

    message: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None


class ErrorResponse(BaseModel):
    """Sobre estándar para respuestas de error."""

    error: ErrorDetail


class EVMIndicatorsSchema(BaseModel):
    """Formato de transferencia para los indicadores EVM."""

    bac: float
    pv: float
    ev: float
    ac: float
    cv: float
    sv: float
    cpi: float | None
    spi: float | None
    eac: float | None
    vac: float | None
    cpi_status: str
    spi_status: str
    cpi_label: str
    spi_label: str

    model_config = ConfigDict(from_attributes=True)
