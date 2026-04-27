"""Tests de integración para los endpoints de proyectos.

Cada test verifica un flujo HTTP end-to-end: request → router → servicio →
repositorio → BD → respuesta. La BD es PostgreSQL real (no un mock) para
garantizar que las consultas SQLAlchemy funcionan en producción.
"""

import pytest
from httpx import AsyncClient


BASE = "/api/v1/projects"

CREATE_PAYLOAD = {
    "name": "Proyecto Test",
    "description": "Descripción de prueba",
    "status_date": "2024-06-30",
}


@pytest.fixture
async def created_project(async_client: AsyncClient) -> dict:
    """Crea un proyecto de apoyo y devuelve su body JSON para reutilizar en tests."""
    resp = await async_client.post(BASE, json=CREATE_PAYLOAD)
    assert resp.status_code == 201
    return resp.json()["data"]


class TestCreateProject:
    async def test_returns_201_with_project_data(self, async_client: AsyncClient):
        resp = await async_client.post(BASE, json=CREATE_PAYLOAD)

        assert resp.status_code == 201
        body = resp.json()["data"]
        assert body["name"] == CREATE_PAYLOAD["name"]
        assert body["description"] == CREATE_PAYLOAD["description"]
        assert body["status_date"] == CREATE_PAYLOAD["status_date"]
        assert body["activity_count"] == 0
        assert "id" in body

    async def test_name_required(self, async_client: AsyncClient):
        resp = await async_client.post(BASE, json={"status_date": "2024-01-01"})

        assert resp.status_code == 422

    async def test_status_date_required(self, async_client: AsyncClient):
        resp = await async_client.post(BASE, json={"name": "Sin fecha"})

        assert resp.status_code == 422


class TestListProjects:
    async def test_returns_200_empty_list(self, async_client: AsyncClient):
        resp = await async_client.get(BASE)

        assert resp.status_code == 200
        assert resp.json()["data"] == []

    async def test_returns_created_project(
        self, async_client: AsyncClient, created_project: dict
    ):
        resp = await async_client.get(BASE)

        assert resp.status_code == 200
        ids = [p["id"] for p in resp.json()["data"]]
        assert created_project["id"] in ids


class TestGetProject:
    async def test_returns_200_with_evm_indicators(
        self, async_client: AsyncClient, created_project: dict
    ):
        resp = await async_client.get(f"{BASE}/{created_project['id']}")

        assert resp.status_code == 200
        body = resp.json()["data"]
        assert body["id"] == created_project["id"]
        assert "indicators" in body
        assert "activities" in body
        # Sin actividades todos los indicadores monetarios son 0
        indicators = body["indicators"]
        assert indicators["bac"] == 0
        assert indicators["pv"] == 0
        assert indicators["ev"] == 0
        assert indicators["cpi"] is None
        assert indicators["spi"] is None

    async def test_returns_404_for_missing_project(self, async_client: AsyncClient):
        resp = await async_client.get(f"{BASE}/00000000-0000-0000-0000-000000000000")

        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "PROJECT_NOT_FOUND"


class TestUpdateProject:
    async def test_returns_200_with_updated_fields(
        self, async_client: AsyncClient, created_project: dict
    ):
        resp = await async_client.put(
            f"{BASE}/{created_project['id']}",
            json={"name": "Nombre Actualizado"},
        )

        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "Nombre Actualizado"

    async def test_returns_404_for_missing_project(self, async_client: AsyncClient):
        resp = await async_client.put(
            f"{BASE}/00000000-0000-0000-0000-000000000000",
            json={"name": "No existe"},
        )

        assert resp.status_code == 404


class TestDeleteProject:
    async def test_returns_200_on_successful_delete(
        self, async_client: AsyncClient, created_project: dict
    ):
        resp = await async_client.delete(f"{BASE}/{created_project['id']}")

        assert resp.status_code == 200
        assert "message" in resp.json()

    async def test_project_is_gone_after_delete(
        self, async_client: AsyncClient, created_project: dict
    ):
        await async_client.delete(f"{BASE}/{created_project['id']}")
        resp = await async_client.get(f"{BASE}/{created_project['id']}")

        assert resp.status_code == 404

    async def test_returns_404_for_missing_project(self, async_client: AsyncClient):
        resp = await async_client.delete(f"{BASE}/00000000-0000-0000-0000-000000000000")

        assert resp.status_code == 404


class TestGetProjectIndicators:
    async def test_returns_evm_indicators(
        self, async_client: AsyncClient, created_project: dict
    ):
        resp = await async_client.get(f"{BASE}/{created_project['id']}/indicators")

        assert resp.status_code == 200
        body = resp.json()["data"]
        assert body["project_id"] == created_project["id"]
        assert "indicators" in body
        assert body["activity_count"] == 0

    async def test_returns_404_for_missing_project(self, async_client: AsyncClient):
        resp = await async_client.get(
            f"{BASE}/00000000-0000-0000-0000-000000000000/indicators"
        )

        assert resp.status_code == 404


class TestEVMCalculationIntegration:
    """Verifica que los indicadores EVM calculados son correctos end-to-end."""

    async def test_evm_after_activity_creation(self, async_client: AsyncClient):
        """Crea un proyecto con una actividad y verifica los indicadores EVM calculados."""
        create_resp = await async_client.post(BASE, json=CREATE_PAYLOAD)
        project_id = create_resp.json()["data"]["id"]

        activity_payload = {
            "name": "Actividad EVM",
            "bac": 10000,
            "planned_percent": 60,
            "actual_percent": 40,
            "actual_cost": 5500,
        }
        await async_client.post(
            f"{BASE}/{project_id}/activities", json=activity_payload
        )

        resp = await async_client.get(f"{BASE}/{project_id}")
        indicators = resp.json()["data"]["indicators"]

        # Verificación con los valores del ejemplo canónico del calculador
        assert indicators["pv"] == pytest.approx(6000)
        assert indicators["ev"] == pytest.approx(4000)
        assert indicators["ac"] == pytest.approx(5500)
        assert indicators["cv"] == pytest.approx(-1500)
        assert indicators["sv"] == pytest.approx(-2000)
        assert indicators["cpi"] == pytest.approx(4000 / 5500)
        assert indicators["spi"] == pytest.approx(4000 / 6000)
        assert indicators["cpi_status"] == "OVER_BUDGET"
        assert indicators["spi_status"] == "BEHIND_SCHEDULE"
