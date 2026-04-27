"""Constantes para el cálculo e interpretación del EVM.

Todos los valores se extraen a este módulo para que no existan números
ni cadenas mágicas dentro del calculador. Los tests pueden importarlos,
pero deben afirmar comportamiento, no los valores de las constantes.
"""

from typing import Final

PERCENT_DIVISOR: Final[float] = 100.0
PERFECT_INDEX: Final[float] = 1.0
AT_RISK_THRESHOLD: Final[float] = 0.9
PERFECT_INDEX_TOLERANCE: Final[float] = 1e-9

STATUS_UNDER_BUDGET: Final[str] = "UNDER_BUDGET"
STATUS_ON_BUDGET: Final[str] = "ON_BUDGET"
STATUS_AT_RISK: Final[str] = "AT_RISK"
STATUS_OVER_BUDGET: Final[str] = "OVER_BUDGET"

STATUS_AHEAD_OF_SCHEDULE: Final[str] = "AHEAD_OF_SCHEDULE"
STATUS_ON_SCHEDULE: Final[str] = "ON_SCHEDULE"
STATUS_BEHIND_SCHEDULE: Final[str] = "BEHIND_SCHEDULE"

STATUS_UNDEFINED: Final[str] = "UNDEFINED"

CPI_LABELS: Final[dict[str, str]] = {
    STATUS_UNDER_BUDGET: "Bajo presupuesto — eficiente en costos",
    STATUS_ON_BUDGET: "En presupuesto",
    STATUS_AT_RISK: "Leve sobrecosto — en zona de alerta",
    STATUS_OVER_BUDGET: "Sobre presupuesto — acción requerida",
    STATUS_UNDEFINED: "Sin datos suficientes para calcular",
}

SPI_LABELS: Final[dict[str, str]] = {
    STATUS_AHEAD_OF_SCHEDULE: "Adelantado",
    STATUS_ON_SCHEDULE: "En tiempo",
    STATUS_AT_RISK: "Leve retraso — en zona de alerta",
    STATUS_BEHIND_SCHEDULE: "Atrasado — acción requerida",
    STATUS_UNDEFINED: "Sin datos suficientes para calcular",
}

NO_ACTIVITIES_LABEL: Final[str] = "Sin actividades registradas"
