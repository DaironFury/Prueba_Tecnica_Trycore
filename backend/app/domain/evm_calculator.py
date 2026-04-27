"""Motor de cálculo EVM puro.

Este módulo es el núcleo de la lógica de negocio. DEBE permanecer libre de
importaciones de FastAPI, SQLAlchemy, modelos Pydantic o cualquier operación
de E/S. Ese aislamiento es lo que permite probar el calculador con cobertura
del 100% sin fixtures, mocks ni base de datos.
"""

import math

from app.domain.constants import (
    AT_RISK_THRESHOLD,
    CPI_LABELS,
    NO_ACTIVITIES_LABEL,
    PERCENT_DIVISOR,
    PERFECT_INDEX,
    PERFECT_INDEX_TOLERANCE,
    SPI_LABELS,
    STATUS_AHEAD_OF_SCHEDULE,
    STATUS_AT_RISK,
    STATUS_BEHIND_SCHEDULE,
    STATUS_ON_BUDGET,
    STATUS_ON_SCHEDULE,
    STATUS_OVER_BUDGET,
    STATUS_UNDEFINED,
    STATUS_UNDER_BUDGET,
)
from app.domain.models.activity import ActivityInput, EVMIndicators


def _safe_divide(numerator: float, denominator: float) -> float | None:
    """Devuelve numerador / denominador, o None cuando el resultado no está definido.

    Un resultado `None` representa un indicador sin valor significativo
    (por ejemplo, CPI cuando el costo real es cero). Retornar `None` en
    vez de `Infinity` o `NaN` mantiene la salida JSON válida y predecible.
    """
    if denominator == 0:
        return None
    result = numerator / denominator
    if math.isinf(result) or math.isnan(result):  # pragma: no cover
        return None
    return result


def _calculate_pv(bac: float, planned_percent: float) -> float:
    return (planned_percent / PERCENT_DIVISOR) * bac


def _calculate_ev(bac: float, actual_percent: float) -> float:
    return (actual_percent / PERCENT_DIVISOR) * bac


def _calculate_eac(bac: float, cpi: float | None) -> float | None:
    """EAC = BAC / CPI, indefinido cuando CPI es None o cero."""
    if cpi is None or cpi == 0:
        return None
    return bac / cpi


def _calculate_vac(bac: float, eac: float | None) -> float | None:
    """VAC = BAC - EAC, indefinido cuando EAC es indefinido."""
    if eac is None:
        return None
    return bac - eac


def _is_perfect(index_value: float) -> bool:
    """Retorna True cuando un índice es numéricamente equivalente a 1.0.

    Usa `math.isclose` para que resultados de aritmética flotante como
    `0.9999999999999998` sean reconocidos como un índice perfecto.
    """
    return math.isclose(
        index_value,
        PERFECT_INDEX,
        rel_tol=PERFECT_INDEX_TOLERANCE,
    )


def interpret_cpi(cpi: float | None) -> tuple[str, str]:
    """Retorna el par (código_de_estado, etiqueta_legible) para un valor de CPI."""
    if cpi is None:
        return STATUS_UNDEFINED, CPI_LABELS[STATUS_UNDEFINED]
    if _is_perfect(cpi):
        return STATUS_ON_BUDGET, CPI_LABELS[STATUS_ON_BUDGET]
    if cpi > PERFECT_INDEX:
        return STATUS_UNDER_BUDGET, CPI_LABELS[STATUS_UNDER_BUDGET]
    if cpi >= AT_RISK_THRESHOLD:
        return STATUS_AT_RISK, CPI_LABELS[STATUS_AT_RISK]
    return STATUS_OVER_BUDGET, CPI_LABELS[STATUS_OVER_BUDGET]


def interpret_spi(spi: float | None) -> tuple[str, str]:
    """Retorna el par (código_de_estado, etiqueta_legible) para un valor de SPI."""
    if spi is None:
        return STATUS_UNDEFINED, SPI_LABELS[STATUS_UNDEFINED]
    if _is_perfect(spi):
        return STATUS_ON_SCHEDULE, SPI_LABELS[STATUS_ON_SCHEDULE]
    if spi > PERFECT_INDEX:
        return STATUS_AHEAD_OF_SCHEDULE, SPI_LABELS[STATUS_AHEAD_OF_SCHEDULE]
    if spi >= AT_RISK_THRESHOLD:
        return STATUS_AT_RISK, SPI_LABELS[STATUS_AT_RISK]
    return STATUS_BEHIND_SCHEDULE, SPI_LABELS[STATUS_BEHIND_SCHEDULE]


def _build_indicators(
    bac: float,
    pv: float,
    ev: float,
    ac: float,
) -> EVMIndicators:
    """Ensambla el conjunto completo de indicadores a partir de los cuatro valores primarios."""
    cv = ev - ac
    sv = ev - pv

    cpi = _safe_divide(ev, ac)
    spi = _safe_divide(ev, pv)

    eac = _calculate_eac(bac, cpi)
    vac = _calculate_vac(bac, eac)

    cpi_status, cpi_label = interpret_cpi(cpi)
    spi_status, spi_label = interpret_spi(spi)

    return EVMIndicators(
        bac=bac,
        pv=pv,
        ev=ev,
        ac=ac,
        cv=cv,
        sv=sv,
        cpi=cpi,
        spi=spi,
        eac=eac,
        vac=vac,
        cpi_status=cpi_status,
        spi_status=spi_status,
        cpi_label=cpi_label,
        spi_label=spi_label,
    )


def calculate_activity_indicators(activity: ActivityInput) -> EVMIndicators:
    """Calcula los ocho indicadores EVM para una actividad individual.

    Los casos borde producen `None` en los indicadores afectados en vez de
    lanzar excepciones o retornar `Infinity`/`NaN`:

    - `actual_cost == 0`        → `cpi`, `eac`, `vac` son `None`
    - `planned_percent == 0`    → `spi` es `None`
    - `actual_percent == 0`     → `cpi == 0`, `eac` y `vac` son `None`
    """
    pv = _calculate_pv(activity.bac, activity.planned_percent)
    ev = _calculate_ev(activity.bac, activity.actual_percent)
    return _build_indicators(
        bac=activity.bac,
        pv=pv,
        ev=ev,
        ac=activity.actual_cost,
    )


def calculate_project_indicators(activities: list[ActivityInput]) -> EVMIndicators:
    """Agrega valores absolutos de las actividades y deriva los índices del proyecto.

    Los índices (CPI, SPI, EAC) se calculan desde los valores absolutos
    agregados; NUNCA son el promedio de los índices individuales de cada
    actividad. Promediar ignoraría el peso relativo (BAC) de cada actividad.

    Cuando la lista de actividades está vacía, todos los campos monetarios
    son cero y los índices son `None` con una etiqueta `NO_ACTIVITIES_LABEL`.
    """
    if not activities:
        return EVMIndicators(
            bac=0.0,
            pv=0.0,
            ev=0.0,
            ac=0.0,
            cv=0.0,
            sv=0.0,
            cpi=None,
            spi=None,
            eac=None,
            vac=None,
            cpi_status=STATUS_UNDEFINED,
            spi_status=STATUS_UNDEFINED,
            cpi_label=NO_ACTIVITIES_LABEL,
            spi_label=NO_ACTIVITIES_LABEL,
        )

    total_bac = sum(activity.bac for activity in activities)
    total_pv = sum(_calculate_pv(a.bac, a.planned_percent) for a in activities)
    total_ev = sum(_calculate_ev(a.bac, a.actual_percent) for a in activities)
    total_ac = sum(activity.actual_cost for activity in activities)

    return _build_indicators(
        bac=total_bac,
        pv=total_pv,
        ev=total_ev,
        ac=total_ac,
    )
