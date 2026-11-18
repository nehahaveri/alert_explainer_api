from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app


ALERT = {
    "title": "High CPU usage",
    "severity": "critical",
    "source": "server-1",
    "metric_name": "cpu_usage",
    "metric_value": 95.0,
    "threshold": 80.0,
}


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        with session_factory() as session:
            yield session

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        engine.dispose()


def test_create_alert(client):
    response = client.post("/alerts/", json=ALERT)

    assert response.status_code == 201
    alert = response.json()
    assert alert.items() >= ALERT.items()
    assert isinstance(alert["id"], int)
    assert datetime.fromisoformat(alert["created_at"])


def test_list_alerts(client):
    assert client.get("/alerts/").json() == []
    first = client.post("/alerts/", json=ALERT).json()
    second = client.post("/alerts/", json={**ALERT, "title": "Second alert"}).json()

    response = client.get("/alerts/")

    assert response.status_code == 200
    assert response.json() == [first, second]


def test_get_alert_by_id(client):
    created = client.post("/alerts/", json=ALERT).json()

    response = client.get(f"/alerts/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created
    assert client.get("/alerts/999").status_code == 404


def test_explain_alert(client):
    created = client.post("/alerts/", json=ALERT).json()

    for method in (client.get, client.post):
        response = method(f"/alerts/{created['id']}/explain")

        assert response.status_code == 200
        explanation = response.json()
        assert explanation["alert_id"] == created["id"]
        assert ALERT["severity"] in explanation["explanation"]
        assert ALERT["metric_name"] in explanation["explanation"]
        assert datetime.fromisoformat(explanation["generated_at"])
        assert method("/alerts/999/explain").status_code == 404


def test_explain_alert_acknowledgement_defaults_when_unresolved(
    client: TestClient,
) -> None:
    alert = _create_alert(client, severity="critical")

    response = client.post(f"/alerts/{alert['id']}/explain")

    assert response.status_code == 200
    assert response.json()["explanation"].endswith(
        "Acknowledged by: Not yet acknowledged."
    )

# --- Edge cases added manually --- 

def _create_alert(client: TestClient, **overrides: str | float) -> dict: 

    """Create an alert through the API and return its JSON response.""" 

    payload: dict[str, str | float] = { 

        "title": "Test alert", 

        "severity": "warning", 

        "source": "test-source", 

        "metric_name": "test_metric", 

        "metric_value": 50.0, 

        "threshold": 40.0, 

    } 

    payload.update(overrides) 

    response = client.post("/alerts", json=payload) 

    assert response.status_code == 201 

    return response.json() 

  

  

def test_explain_alert_for_nonexistent_id_returns_404(client: TestClient) -> None: 

    response = client.post("/alerts/999/explain") 

  

    assert response.status_code == 404 

    assert response.json()["detail"] == "Alert not found" 

  

  

def test_explain_alert_when_metric_is_below_threshold( 

    client: TestClient, 

) -> None: 

    alert = _create_alert( 

        client, 

        title="Connection pool below minimum", 

        severity="warning", 

        source="db-pool", 

        metric_name="active_connections", 

        metric_value=2, 

        threshold=10, 

    ) 

  

    response = client.post(f"/alerts/{alert['id']}/explain") 

  

    assert response.status_code == 200 

    assert "fell below its threshold" in response.json()["explanation"] 

  

  

def test_explain_alert_with_zero_threshold_does_not_crash( 

    client: TestClient, 

) -> None: 

    alert = _create_alert( 

        client, 

        title="Unexpected traffic on idle endpoint", 

        severity="info", 

        source="edge-cache", 

        metric_name="request_count", 

        metric_value=5, 

        threshold=0, 

    ) 

  

    response = client.post(f"/alerts/{alert['id']}/explain") 

  

    assert response.status_code == 200 

    assert "threshold of 0.0" in response.json()["explanation"] 

