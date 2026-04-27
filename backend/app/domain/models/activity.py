"""Dataclasses de dominio puro para actividades e indicadores EVM.

Estos tipos no contienen ninguna dependencia de persistencia ni de HTTP.
Existen para que el calculador EVM opere sobre valores simples sin arrastrar
SQLAlchemy ni Pydantic al núcleo del cálculo.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ActivityInput:
    """Cinco campos de entrada que describen completamente una actividad para el cálculo EVM.

    Los porcentajes se expresan en el rango 0-100, no como decimales 0-1.
    La normalización ocurre dentro del calculador, en un único lugar.
    """

    bac: float
    planned_percent: float
    actual_percent: float
    actual_cost: float


@dataclass(frozen=True)
class EVMIndicators:
    """Resultado de un cálculo EVM para una actividad individual o un proyecto.

    Los campos opcionales contienen `None` cuando la fórmula correspondiente
    no está definida (por ejemplo, `cpi` cuando `actual_cost == 0`). El
    frontend renderiza `None` como `N/A` en vez de `Infinity` o `0`.
    """

    pv: float
    ev: float
    ac: float
    bac: float
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
