from unittest.mock import patch
from fastapi.testclient import TestClient
from src.main import create_app


def test_health_live() -> None:
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/health/live")
        assert r.status_code == 200
        assert r.json()["status"] == "alive"


def test_health_ready_without_db_mock_succeeds_when_db_ok() -> None:
    app = create_app()
    with (
        patch(
            "src.api.controllers.health_controller.check_database_health",
            return_value=True,
        ) as mocked_check,
        TestClient(app) as client,
    ):
        r = client.get("/health/ready")
        assert r.status_code == 200
        mocked_check.assert_called_once()


def test_health_ready_503_when_db_down() -> None:
    app = create_app()
    with (
        patch(
            "src.api.controllers.health_controller.check_database_health",
            return_value=False,
        ) as mocked_check,
        TestClient(app) as client,
    ):
        r = client.get("/health/ready")
        assert r.status_code == 503
        assert r.json()["detail"] == "Database unavailable"
        mocked_check.assert_called_once()


def test_metrics_returns_prometheus_text() -> None:
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/metrics")
        assert r.status_code == 200
        assert "text/plain" in r.headers.get("content-type", "")
        payload = r.text
        assert "api_health_checks_total" in payload
        assert "api_readiness_check_duration_seconds" in payload
