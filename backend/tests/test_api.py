"""FastAPI smoke tests."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_neighbourhood_catalogue_is_labelled_demo_data():
    response = client.get("/v1/neighbourhoods")
    assert response.status_code == 200
    assert response.json()["data_status"] == "illustrative_demo_data"

def test_unknown_neighbourhood_returns_404():
    response = client.get("/v1/neighbourhoods/not-a-real-id")
    assert response.status_code == 404
