"""FastAPI smoke tests."""
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.places import CommuteRequest
from app.services.geo import VALHALLA_COSTING

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


def test_supported_modes_map_to_distinct_valhalla_costing_profiles():
    assert VALHALLA_COSTING == {
        "driving": "auto",
        "motorcycle": "motorcycle",
        "scooter": "motor_scooter",
        "cycling": "bicycle",
        "walking": "pedestrian",
    }


def test_photon_results_are_normalised_and_foreign_results_filtered():
    from app.services.geo import _normalise_photon

    payload = {
        "features": [
            {
                "properties": {
                    "name": "Kharghar", "city": "Navi Mumbai",
                    "state": "Maharashtra", "country": "India",
                    "countrycode": "IN", "type": "suburb",
                },
                "geometry": {"coordinates": [73.069, 19.048]},
            },
            {
                "properties": {"name": "Kharghar", "country": "Nepal", "countrycode": "np"},
                "geometry": {"coordinates": [84.0, 28.0]},
            },
        ]
    }
    rows = _normalise_photon(payload)
    assert len(rows) == 1
    assert rows[0]["display_name"] == "Kharghar, Navi Mumbai, Maharashtra, India"
    assert rows[0]["latitude"] == 19.048
    assert rows[0]["longitude"] == 73.069


def test_places_suggest_endpoint_exists(monkeypatch):
    async def fake_suggest(_query):
        return [{
            "display_name": "Kharghar, Navi Mumbai, Maharashtra, India",
            "latitude": 19.048,
            "longitude": 73.069,
            "category": "suburb",
        }]

    monkeypatch.setattr("app.api.routes.places.suggest_places", fake_suggest)
    response = client.get("/v1/places/suggest", params={"q": "Kharghar, India"})
    assert response.status_code == 200
    assert response.json()[0]["display_name"].startswith("Kharghar")


def test_open_meteo_results_are_filtered_to_india(monkeypatch):
    import asyncio
    from app.services import geo

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"results": [
                {"name": "Kharghar", "admin2": "Raigad", "admin1": "Maharashtra",
                 "country": "India", "country_code": "IN", "latitude": 19.04,
                 "longitude": 73.06, "feature_code": "PPL"},
                {"name": "Kharghar", "country": "Nepal", "country_code": "NP",
                 "latitude": 28.0, "longitude": 84.0},
            ]}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(geo.httpx, "AsyncClient", FakeClient)
    rows = asyncio.run(geo._open_meteo_search("Kharghar, Navi Mumbai, India", 6))
    assert len(rows) == 1
    assert rows[0]["display_name"] == "Kharghar, Raigad, Maharashtra, India"
    assert rows[0]["latitude"] == 19.04


def test_search_falls_back_to_open_meteo_when_osm_providers_fail(monkeypatch):
    import asyncio
    from app.services import geo

    async def fail(*args, **kwargs):
        raise RuntimeError("provider unavailable")

    async def fallback(*args, **kwargs):
        return [{"display_name": "Kharghar, Maharashtra, India",
                 "latitude": 19.04, "longitude": 73.06, "category": "PPL"}]

    monkeypatch.setattr(geo, "_photon_search", fail)
    monkeypatch.setattr(geo, "_nominatim_search", fail)
    monkeypatch.setattr(geo, "_open_meteo_search", fallback)
    geo._search_cache.clear()
    rows = asyncio.run(geo.search_places("Kharghar, India"))
    assert rows[0]["display_name"].startswith("Kharghar")
