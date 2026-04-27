"""Tests de integración para los endpoints de actividades.

Valida el CRUD de actividades anidadas bajo proyectos y verifica que el
cálculo EVM del backend produce los indicadores correctos por actividad.
"""

import pytest
from httpx import AsyncClient


PROJECTS_BASE = "/api/v1/projects"
PROJECT_PAYLOAD = {"name": "Proyecto para Actividades", "status_date": "2024-12-31"}

ACTIVITY_PAYLOAD = {
    "name": "Actividad de Prueba",
    "bac": 1000.0,
    "planned_percent": 50.0,
    "actual_percent": 40.0,
    "actual_cost": 600.0,
}


@pytest.fixture
async def project_id(async_client: AsyncClient) -> str:
    """Crea un proyecto de apoyo y devuelve su id."""
    resp = await async_client.post(PROJECTS_BASE, json=PROJECT_PAYLOAD)
    return resp.json()["data"]["id"]


@pytest.fixture
async def created_activity(async_client: AsyncClient, project_id: str) -> dict:
    """Crea una actividad y devuelve su body JSON."""
    url = f"{PROJECTS_BASE}/{project_id}/activities"
    resp = await async_client.post(url, json=ACTIVITY_PAYLOAD)
    assert resp.status_code == 201
    return resp.json()["data"]


class TestCreateActivity:
    async def test_returns_201_with_activity_data(
        self, async_client: AsyncClient, project_id: str
    ):
        resp = await async_client.post(
            f"{PROJECTS_BASE}/{project_id}/activities", json=ACTIVITY_PAYLOAD
        )

        assert resp.status_code == 201
        body = resp.json()["data"]
        assert body["name"] == ACTIVITY_PAYLOAD["name"]
        assert body["bac"] == ACTIVITY_PAYLOAD["bac"]
        assert body["project_id"] == project_id
        assert "indicators" in body
        assert "id" in body

    async def test_evm_indicators_are_calculated_correctly(
        self, async_client: AsyncClient, project_id: str
    ):
        """PV=500, EV=400, CV=-200, SV=-100, CPI=400/600, SPI=0.8."""
        resp = await async_client.post(
            f"{PROJECTS_BASE}/{project_id}/activities", json=ACTIVITY_PAYLOAD
        )

        indicators = resp.json()["data"]["indicators"]
        assert indicators["pv"] == pytest.approx(500)
        assert indicators["ev"] == pytest.approx(400)
        assert indicators["ac"] == pytest.approx(600)
        assert indicators["cv"] == pytest.approx(-200)
        assert indicators["sv"] == pytest.approx(-100)
        assert indicators["cpi"] == pytest.approx(400 / 600)
        assert indicators["spi"] == pytest.approx(0.8)
        assert indicators["eac"] == pytest.approx(1500)
        assert indicators["vac"] == pytest.approx(-500)
        assert indicators["cpi_status"] == "OVER_BUDGET"
        assert indicators["spi_status"] == "BEHIND_SCHEDULE"

    async def test_returns_404_when_project_not_found(self, async_client: AsyncClient):
        resp = await async_client.post(
            f"{PROJECTS_BASE}/00000000-0000-0000-0000-000000000000/activities",
            json=ACTIVITY_PAYLOAD,
        )

        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "PROJECT_NOT_FOUND"

    async def test_validates_negative_bac(
        self, async_client: AsyncClient, project_id: str
    ):
        payload = {**ACTIVITY_PAYLOAD, "bac": -100}
        resp = await async_client.post(
            f"{PROJECTS_BASE}/{project_id}/activities", json=payload
        )

        assert resp.status_code == 422

    async def test_validates_percent_out_of_range(
        self, async_client: AsyncClient, project_id: str
    ):
        payload = {**ACTIVITY_PAYLOAD, "planned_percent": 150}
        resp = await async_client.post(
            f"{PROJECTS_BASE}/{project_id}/activities", json=payload
        )

        assert resp.status_code == 422


class TestUpdateActivity:
    async def test_returns_200_with_updated_fields(
        self,
        async_client: AsyncClient,
        project_id: str,
        created_activity: dict,
    ):
        url = f"{PROJECTS_BASE}/{project_id}/activities/{created_activity['id']}"
        resp = await async_client.put(url, json={"name": "Actividad Renombrada"})

        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "Actividad Renombrada"

    async def test_evm_recalculated_after_update(
        self,
        async_client: AsyncClient,
        project_id: str,
        created_activity: dict,
    ):
        """Actualizar actual_percent debe recalcular EV y todos los índices derivados."""
        url = f"{PROJECTS_BASE}/{project_id}/activities/{created_activity['id']}"
        resp = await async_client.put(url, json={"actual_percent": 80.0})

        indicators = resp.json()["data"]["indicators"]
        # EV = 80% * 1000 = 800; PV = 50% * 1000 = 500; AC = 600
        assert indicators["ev"] == pytest.approx(800)
        assert indicators["sv"] == pytest.approx(300)  # EV - PV = 800 - 500
        assert indicators["cpi"] == pytest.approx(800 / 600)
        assert indicators["cpi_status"] == "UNDER_BUDGET"
        assert indicators["spi_status"] == "AHEAD_OF_SCHEDULE"

    async def test_returns_404_when_activity_not_found(
        self, async_client: AsyncClient, project_id: str
    ):
        url = f"{PROJECTS_BASE}/{project_id}/activities/00000000-0000-0000-0000-000000000000"
        resp = await async_client.put(url, json={"name": "No existe"})

        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "ACTIVITY_NOT_FOUND"

    async def test_returns_404_when_project_not_found(
        self, async_client: AsyncClient, created_activity: dict
    ):
        url = (
            f"{PROJECTS_BASE}/00000000-0000-0000-0000-000000000000"
            f"/activities/{created_activity['id']}"
        )
        resp = await async_client.put(url, json={"name": "Sin proyecto"})

        assert resp.status_code == 404


class TestDeleteActivity:
    async def test_returns_200_on_successful_delete(
        self,
        async_client: AsyncClient,
        project_id: str,
        created_activity: dict,
    ):
        url = f"{PROJECTS_BASE}/{project_id}/activities/{created_activity['id']}"
        resp = await async_client.delete(url)

        assert resp.status_code == 200
        assert "message" in resp.json()

    async def test_project_activity_count_decreases(
        self,
        async_client: AsyncClient,
        project_id: str,
        created_activity: dict,
    ):
        await async_client.delete(
            f"{PROJECTS_BASE}/{project_id}/activities/{created_activity['id']}"
        )
        resp = await async_client.get(f"{PROJECTS_BASE}/{project_id}")

        assert resp.json()["data"]["activities"] == []

    async def test_returns_404_when_activity_not_found(
        self, async_client: AsyncClient, project_id: str
    ):
        url = f"{PROJECTS_BASE}/{project_id}/activities/00000000-0000-0000-0000-000000000000"
        resp = await async_client.delete(url)

        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "ACTIVITY_NOT_FOUND"


class TestActivityBelongsToProject:
    """Garantiza que un activity_id de otro proyecto retorna 404, no datos incorrectos."""

    async def test_cannot_update_activity_from_another_project(
        self, async_client: AsyncClient, created_activity: dict
    ):
        other_project_resp = await async_client.post(
            PROJECTS_BASE, json={"name": "Otro proyecto", "status_date": "2024-01-01"}
        )
        other_id = other_project_resp.json()["data"]["id"]

        url = f"{PROJECTS_BASE}/{other_id}/activities/{created_activity['id']}"
        resp = await async_client.put(url, json={"name": "Intento cross-project"})

        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "ACTIVITY_NOT_IN_PROJECT"
