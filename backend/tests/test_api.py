"""FastAPI smoke tests."""
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.places import CommuteRequest

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


@pytest.mark.parametrize("mode", ["driving", "motorcycle", "scooter", "cycling", "walking"])
def test_commute_request_accepts_supported_travel_modes(mode):
    payload = CommuteRequest(
        origin_lat=19.0, origin_lon=72.0,
        destination_lat=19.1, destination_lon=72.1,
        mode=mode,
    )
    assert payload.mode == mode


@pytest.mark.parametrize("mode", ["public_transport", "transit", "train", "metro"])
def test_commute_request_rejects_unconfigured_transit_modes(mode):
    with pytest.raises(ValidationError):
        CommuteRequest(
            origin_lat=19.0, origin_lon=72.0,
            destination_lat=19.1, destination_lon=72.1,
            mode=mode,
        )
