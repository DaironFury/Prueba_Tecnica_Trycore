"""Tests unitarios para el calculador EVM puro.

Estos tests ejercitan el calculador en completo aislamiento: sin base de
datos, sin HTTP, sin mocks. Si algún test necesita una fixture más allá de
valores simples, algo está mal con la pureza del calculador.
"""

import pytest

from app.domain.constants import (
    CPI_LABELS,
    NO_ACTIVITIES_LABEL,
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
from app.domain.evm_calculator import (
    calculate_activity_indicators,
    calculate_project_indicators,
    interpret_cpi,
    interpret_spi,
)
from app.domain.models.activity import ActivityInput

TOLERANCIA_ABSOLUTA = 1e-6


def _activity(
    bac: float = 1000,
    planned_percent: float = 50,
    actual_percent: float = 40,
    actual_cost: float = 600,
) -> ActivityInput:
    """Construye un ActivityInput con valores predeterminados razonables para los tests."""
    return ActivityInput(
        bac=bac,
        planned_percent=planned_percent,
        actual_percent=actual_percent,
        actual_cost=actual_cost,
    )


class TestActivityCanonicalExamples:
    """Valida el calculador contra casos de referencia resueltos manualmente."""

    def test_ejemplo_documentado_bac_10000(self):
        result = calculate_activity_indicators(
            _activity(bac=10_000, planned_percent=60, actual_percent=40, actual_cost=5_500)
        )

        assert result.pv == pytest.approx(6_000)
        assert result.ev == pytest.approx(4_000)
        assert result.ac == pytest.approx(5_500)
        assert result.bac == pytest.approx(10_000)
        assert result.cv == pytest.approx(-1_500)
        assert result.sv == pytest.approx(-2_000)
        assert result.cpi == pytest.approx(4_000 / 5_500)
        assert result.spi == pytest.approx(4_000 / 6_000)
        assert result.eac == pytest.approx(10_000 / (4_000 / 5_500))
        assert result.vac == pytest.approx(10_000 - 10_000 / (4_000 / 5_500))
        assert result.cpi_status == STATUS_OVER_BUDGET
        assert result.spi_status == STATUS_BEHIND_SCHEDULE

    def test_ejemplo_documentado_bac_1000(self):
        result = calculate_activity_indicators(
            _activity(bac=1_000, planned_percent=50, actual_percent=40, actual_cost=600)
        )

        assert result.pv == pytest.approx(500)
        assert result.ev == pytest.approx(400)
        assert result.cv == pytest.approx(-200)
        assert result.sv == pytest.approx(-100)
        assert result.cpi == pytest.approx(400 / 600)
        assert result.spi == pytest.approx(0.8)
        assert result.eac == pytest.approx(1_500, abs=TOLERANCIA_ABSOLUTA)
        assert result.vac == pytest.approx(-500, abs=TOLERANCIA_ABSOLUTA)
        assert result.cpi_status == STATUS_OVER_BUDGET
        assert result.spi_status == STATUS_BEHIND_SCHEDULE


class TestActivityPerformanceScenarios:
    """Cada régimen de desempeño — bajo, en y sobre presupuesto — por separado."""

    def test_desempeno_perfecto_retorna_en_presupuesto_y_en_tiempo(self):
        result = calculate_activity_indicators(
            _activity(bac=1_000, planned_percent=50, actual_percent=50, actual_cost=500)
        )

        assert result.cv == pytest.approx(0)
        assert result.sv == pytest.approx(0)
        assert result.cpi == pytest.approx(1.0)
        assert result.spi == pytest.approx(1.0)
        assert result.eac == pytest.approx(1_000)
        assert result.vac == pytest.approx(0)
        assert result.cpi_status == STATUS_ON_BUDGET
        assert result.spi_status == STATUS_ON_SCHEDULE

    def test_bajo_presupuesto_y_adelantado(self):
        result = calculate_activity_indicators(
            _activity(bac=1_000, planned_percent=40, actual_percent=60, actual_cost=400)
        )

        assert result.cpi > 1.0
        assert result.spi > 1.0
        assert result.cv > 0
        assert result.sv > 0
        assert result.vac > 0
        assert result.cpi_status == STATUS_UNDER_BUDGET
        assert result.spi_status == STATUS_AHEAD_OF_SCHEDULE


class TestActivityEdgeCases:
    """Los casos borde requeridos explícitamente por el brief técnico."""

    def test_costo_real_cero_deja_cpi_eac_y_vac_indefinidos(self):
        result = calculate_activity_indicators(
            _activity(bac=1_000, planned_percent=50, actual_percent=40, actual_cost=0)
        )

        assert result.cpi is None
        assert result.eac is None
        assert result.vac is None
        assert result.spi is not None
        assert result.cpi_status == STATUS_UNDEFINED
        assert result.cpi_label == CPI_LABELS[STATUS_UNDEFINED]

    def test_porcentaje_planificado_cero_deja_spi_indefinido(self):
        result = calculate_activity_indicators(
            _activity(bac=1_000, planned_percent=0, actual_percent=40, actual_cost=300)
        )

        assert result.pv == 0
        assert result.spi is None
        assert result.cpi is not None
        assert result.spi_status == STATUS_UNDEFINED
        assert result.spi_label == SPI_LABELS[STATUS_UNDEFINED]

    def test_porcentaje_real_cero_con_costo_positivo_deja_eac_indefinido(self):
        result = calculate_activity_indicators(
            _activity(bac=1_000, planned_percent=50, actual_percent=0, actual_cost=300)
        )

        assert result.ev == 0
        assert result.cpi == 0
        assert result.eac is None
        assert result.vac is None
        assert result.cpi_status == STATUS_OVER_BUDGET

    def test_todas_las_entradas_cero_retorna_indices_indefinidos(self):
        result = calculate_activity_indicators(
            _activity(bac=0, planned_percent=0, actual_percent=0, actual_cost=0)
        )

        assert result.pv == 0
        assert result.ev == 0
        assert result.cv == 0
        assert result.sv == 0
        assert result.cpi is None
        assert result.spi is None
        assert result.eac is None
        assert result.vac is None
        assert result.cpi_status == STATUS_UNDEFINED
        assert result.spi_status == STATUS_UNDEFINED


class TestCPIInterpretation:
    """Validación límite a límite de la función de estado del CPI."""

    @pytest.mark.parametrize(
        ("cpi_value", "expected_status"),
        [
            (None, STATUS_UNDEFINED),
            (0.0, STATUS_OVER_BUDGET),
            (0.5, STATUS_OVER_BUDGET),
            (0.89, STATUS_OVER_BUDGET),
            (0.9, STATUS_AT_RISK),
            (0.95, STATUS_AT_RISK),
            (0.999_999_999_9, STATUS_ON_BUDGET),
            (1.0, STATUS_ON_BUDGET),
            (1.000_000_000_1, STATUS_ON_BUDGET),
            (1.01, STATUS_UNDER_BUDGET),
            (2.0, STATUS_UNDER_BUDGET),
        ],
    )
    def test_umbrales_de_estado(self, cpi_value, expected_status):
        status, label = interpret_cpi(cpi_value)
        assert status == expected_status
        assert label == CPI_LABELS[expected_status]


class TestSPIInterpretation:
    """Validación límite a límite de la función de estado del SPI."""

    @pytest.mark.parametrize(
        ("spi_value", "expected_status"),
        [
            (None, STATUS_UNDEFINED),
            (0.0, STATUS_BEHIND_SCHEDULE),
            (0.5, STATUS_BEHIND_SCHEDULE),
            (0.89, STATUS_BEHIND_SCHEDULE),
            (0.9, STATUS_AT_RISK),
            (0.95, STATUS_AT_RISK),
            (0.999_999_999_9, STATUS_ON_SCHEDULE),
            (1.0, STATUS_ON_SCHEDULE),
            (1.000_000_000_1, STATUS_ON_SCHEDULE),
            (1.01, STATUS_AHEAD_OF_SCHEDULE),
            (2.0, STATUS_AHEAD_OF_SCHEDULE),
        ],
    )
    def test_umbrales_de_estado(self, spi_value, expected_status):
        status, label = interpret_spi(spi_value)
        assert status == expected_status
        assert label == SPI_LABELS[expected_status]


class TestProjectAggregationEmpty:
    """Proyecto sin actividades — estado UNDEFINED explícito."""

    def test_proyecto_vacio_retorna_monetarios_en_cero_e_indices_indefinidos(self):
        result = calculate_project_indicators([])

        assert result.bac == 0
        assert result.pv == 0
        assert result.ev == 0
        assert result.ac == 0
        assert result.cv == 0
        assert result.sv == 0
        assert result.cpi is None
        assert result.spi is None
        assert result.eac is None
        assert result.vac is None
        assert result.cpi_status == STATUS_UNDEFINED
        assert result.spi_status == STATUS_UNDEFINED
        assert result.cpi_label == NO_ACTIVITIES_LABEL
        assert result.spi_label == NO_ACTIVITIES_LABEL


class TestProjectAggregationSingleActivity:
    """Un proyecto de una sola actividad debe ser igual al cálculo individual."""

    def test_actividad_unica_coincide_con_indicadores_de_actividad(self):
        activity = _activity(bac=2_000, planned_percent=70, actual_percent=50, actual_cost=900)

        from_activity = calculate_activity_indicators(activity)
        from_project = calculate_project_indicators([activity])

        assert from_project.pv == pytest.approx(from_activity.pv)
        assert from_project.ev == pytest.approx(from_activity.ev)
        assert from_project.ac == pytest.approx(from_activity.ac)
        assert from_project.bac == pytest.approx(from_activity.bac)
        assert from_project.cpi == pytest.approx(from_activity.cpi)
        assert from_project.spi == pytest.approx(from_activity.spi)
        assert from_project.eac == pytest.approx(from_activity.eac)
        assert from_project.vac == pytest.approx(from_activity.vac)


class TestProjectAggregationMultipleActivities:
    """La agregación debe sumar valores absolutos, nunca promediar índices."""

    def test_suma_valores_absolutos_entre_actividades(self):
        activities = [
            _activity(bac=10_000, planned_percent=60, actual_percent=40, actual_cost=5_500),
            _activity(bac=5_000, planned_percent=80, actual_percent=70, actual_cost=4_000),
        ]

        result = calculate_project_indicators(activities)

        assert result.bac == pytest.approx(15_000)
        assert result.pv == pytest.approx(0.60 * 10_000 + 0.80 * 5_000)
        assert result.ev == pytest.approx(0.40 * 10_000 + 0.70 * 5_000)
        assert result.ac == pytest.approx(5_500 + 4_000)

    def test_indices_son_ponderados_no_promediados(self):
        """Una actividad pequeña con buen desempeño no debe enmascarar una grande con problemas."""
        large_struggling = _activity(
            bac=100_000, planned_percent=50, actual_percent=40, actual_cost=60_000
        )
        small_succeeding = _activity(
            bac=1_000, planned_percent=50, actual_percent=80, actual_cost=400
        )

        result = calculate_project_indicators([large_struggling, small_succeeding])

        expected_total_ev = 0.40 * 100_000 + 0.80 * 1_000
        expected_total_ac = 60_000 + 400
        expected_cpi = expected_total_ev / expected_total_ac

        naive_average_cpi = (
            (0.40 * 100_000 / 60_000) + (0.80 * 1_000 / 400)
        ) / 2

        assert result.cpi == pytest.approx(expected_cpi)
        assert result.cpi != pytest.approx(naive_average_cpi)
        assert result.cpi_status == STATUS_OVER_BUDGET

    def test_todas_las_actividades_con_costo_cero_producen_cpi_indefinido(self):
        activities = [
            _activity(bac=1_000, planned_percent=50, actual_percent=30, actual_cost=0),
            _activity(bac=2_000, planned_percent=40, actual_percent=20, actual_cost=0),
        ]

        result = calculate_project_indicators(activities)

        assert result.ac == 0
        assert result.cpi is None
        assert result.eac is None
        assert result.vac is None
        assert result.spi is not None


class TestPurity:
    """El calculador debe ser una función pura de sus entradas."""

    def test_misma_entrada_produce_misma_salida(self):
        activity = _activity(bac=10_000, planned_percent=60, actual_percent=40, actual_cost=5_500)

        first = calculate_activity_indicators(activity)
        second = calculate_activity_indicators(activity)

        assert first == second

    def test_dataclass_de_entrada_es_inmutable(self):
        activity = _activity()
        with pytest.raises(Exception):
            activity.bac = 9_999  # el dataclass frozen prohíbe la mutación


class TestMathematicalProperties:
    """Invariantes algebraicos que deben cumplirse para cualquier entrada válida.

    Estos tests verifican *propiedades* más que números específicos. Detectan
    regresiones que los tests solo aritméticos no capturan, como un cambio
    de signo o un error de unidad en la fórmula del EAC.
    """

    def test_cpi_igual_a_uno_cuando_ev_igual_a_ac(self):
        """Ley de identidad del costo: mismo valor ganado que gastado → CPI = 1."""
        result = calculate_activity_indicators(
            _activity(bac=1_000, planned_percent=50, actual_percent=70, actual_cost=700)
        )
        assert result.ev == pytest.approx(result.ac)
        assert result.cpi == pytest.approx(1.0)

    def test_spi_igual_a_uno_cuando_ev_igual_a_pv(self):
        """Ley de identidad del cronograma: lo planificado y lo ganado coinciden → SPI = 1."""
        result = calculate_activity_indicators(
            _activity(bac=1_000, planned_percent=60, actual_percent=60, actual_cost=900)
        )
        assert result.ev == pytest.approx(result.pv)
        assert result.spi == pytest.approx(1.0)

    @pytest.mark.parametrize(
        ("actual_percent", "actual_cost"),
        [
            (60, 400),  # CV positivo → CPI > 1
            (40, 400),  # CV cero → CPI = 1
            (40, 600),  # CV negativo → CPI < 1
        ],
    )
    def test_cv_y_cpi_menos_uno_comparten_signo(self, actual_percent, actual_cost):
        """Coherencia de signos: CV > 0 ⟺ CPI > 1; CV < 0 ⟺ CPI < 1."""
        result = calculate_activity_indicators(
            _activity(
                bac=1_000,
                planned_percent=50,
                actual_percent=actual_percent,
                actual_cost=actual_cost,
            )
        )
        if result.cv > 0:
            assert result.cpi > 1.0
        elif result.cv < 0:
            assert result.cpi < 1.0
        else:
            assert result.cpi == pytest.approx(1.0)

    @pytest.mark.parametrize(
        ("planned_percent", "actual_percent"),
        [
            (40, 60),  # SV positivo → SPI > 1
            (50, 50),  # SV cero → SPI = 1
            (60, 40),  # SV negativo → SPI < 1
        ],
    )
    def test_sv_y_spi_menos_uno_comparten_signo(self, planned_percent, actual_percent):
        """Coherencia de signos: SV > 0 ⟺ SPI > 1; SV < 0 ⟺ SPI < 1."""
        result = calculate_activity_indicators(
            _activity(
                bac=1_000,
                planned_percent=planned_percent,
                actual_percent=actual_percent,
                actual_cost=500,
            )
        )
        if result.sv > 0:
            assert result.spi > 1.0
        elif result.sv < 0:
            assert result.spi < 1.0
        else:
            assert result.spi == pytest.approx(1.0)

    def test_eac_por_cpi_recupera_bac(self):
        """Inversión algebraica: BAC = EAC × CPI por construcción del EAC."""
        result = calculate_activity_indicators(
            _activity(bac=10_000, planned_percent=60, actual_percent=40, actual_cost=5_500)
        )
        assert result.eac is not None
        assert result.cpi is not None
        assert result.eac * result.cpi == pytest.approx(result.bac)

    def test_eac_mas_vac_es_igual_a_bac(self):
        """Identidad complementaria: VAC = BAC − EAC, entonces EAC + VAC = BAC."""
        result = calculate_activity_indicators(
            _activity(bac=10_000, planned_percent=60, actual_percent=40, actual_cost=5_500)
        )
        assert result.eac is not None
        assert result.vac is not None
        assert result.eac + result.vac == pytest.approx(result.bac)

    def test_escalar_entradas_monetarias_preserva_los_indices(self):
        """Linealidad: multiplicar BAC y AC por k deja CPI y SPI sin cambio.

        Protege contra suposiciones de escala hardcodeadas accidentalmente
        (p.ej. tratar montos como centavos en un lugar y pesos en otro).
        """
        scale = 1_000
        base = calculate_activity_indicators(
            _activity(bac=10, planned_percent=60, actual_percent=40, actual_cost=5.5)
        )
        scaled = calculate_activity_indicators(
            _activity(
                bac=10 * scale,
                planned_percent=60,
                actual_percent=40,
                actual_cost=5.5 * scale,
            )
        )
        assert scaled.cpi == pytest.approx(base.cpi)
        assert scaled.spi == pytest.approx(base.spi)
        assert scaled.pv == pytest.approx(base.pv * scale)
        assert scaled.ev == pytest.approx(base.ev * scale)

    def test_actividad_con_bac_cero_no_altera_indices_del_proyecto(self):
        """Una actividad sin presupuesto no debe afectar la agregación del proyecto."""
        meaningful = _activity(bac=10_000, planned_percent=60, actual_percent=40, actual_cost=5_500)
        placeholder = _activity(bac=0, planned_percent=0, actual_percent=0, actual_cost=0)

        without_placeholder = calculate_project_indicators([meaningful])
        with_placeholder = calculate_project_indicators([meaningful, placeholder])

        assert with_placeholder.bac == pytest.approx(without_placeholder.bac)
        assert with_placeholder.cpi == pytest.approx(without_placeholder.cpi)
        assert with_placeholder.spi == pytest.approx(without_placeholder.spi)
