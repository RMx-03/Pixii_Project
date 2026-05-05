"""Integration tests for diagnostic endpoints."""

from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_run_get_and_export_report() -> None:
    payload = {
        "target_url": "https://www.amazon.com/dp/B000TEST",
        "query": "best magnesium supplement for seniors",
        "competitor_mode": "manual",
        "competitor_urls": ["https://www.amazon.com/dp/B000ABC"],
    }
    run_response = client.post("/api/v1/diagnostics/run", json=payload)
    assert run_response.status_code == 200
    run = run_response.json()
    assert run["run_id"]
    run_id = run["run_id"]

    get_response = client.get(f"/api/v1/diagnostics/runs/{run_id}")
    assert get_response.status_code == 200
    assert get_response.json()["run_id"] == run_id

    export_response = client.get(f"/api/v1/diagnostics/reports/{run_id}/export?format=md")
    assert export_response.status_code == 200
    assert "AEO Report Card" in export_response.text


def test_rerun_returns_delta() -> None:
    baseline_payload = {
        "target_url": "https://www.amazon.com/dp/B000TEST",
        "query": "best magnesium supplement for seniors",
        "competitor_mode": "manual",
        "competitor_urls": ["https://www.amazon.com/dp/B000ABC"],
    }
    baseline = client.post("/api/v1/diagnostics/run", json=baseline_payload).json()
    rerun_payload = {
        "baseline_run_id": baseline["run_id"],
        "target_url": "https://www.amazon.com/dp/B000TEST",
        "query": "best magnesium supplement for seniors",
        "competitor_mode": "manual",
        "competitor_urls": ["https://www.amazon.com/dp/B000ABC"],
    }
    rerun_response = client.post("/api/v1/diagnostics/rerun", json=rerun_payload)
    assert rerun_response.status_code == 200
    body = rerun_response.json()
    assert body["delta"]["baseline_run_id"] == baseline["run_id"]
