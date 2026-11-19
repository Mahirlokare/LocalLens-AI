# LocalLens AI

**Neighbourhood & Commute Intelligence Platform**

LocalLens AI is a decision-support application for comparing neighbourhoods using transparent, source-backed indicators and commute estimates. It is designed to reduce the effort involved in researching an area before renting, buying, studying, or relocating.

> **Current status:** Initial backend foundation. The current API provides health checks and transparent indicator scoring from data supplied by the caller. Live neighbourhood datasets, routing integrations, persistence, frontend, and deployment are not implemented yet.

## Product goals

- Compare neighbourhoods using configurable criteria and weights.
- Show indicator values, source attribution, and data freshness.
- Estimate journeys to user-selected destinations through a routing provider.
- Explain trade-offs without presenting an opaque score as an official rating.
- Generate shareable reports with limitations and provenance.

## Architecture

- **Frontend:** React + TypeScript (planned)
- **API:** Python + FastAPI
- **Data validation:** Pydantic
- **Database:** PostgreSQL + PostGIS (planned)
- **Geospatial UI:** Leaflet + OpenStreetMap (planned)
- **Testing:** Pytest

## Repository layout

```text
backend/
  app/
    api/routes/
    core/
    schemas/
    services/
  tests/
  requirements.txt
  .env.example
  Dockerfile
docker-compose.yml
```

## Run the API locally

Requirements: Python 3.11+

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for interactive API documentation.

## Current API

- `GET /health` — service health.
- `POST /v1/comparisons/score` — calculate a weighted score for supplied neighbourhood indicators.

Scoring inputs must be normalized to the range 0–100. Weights must be non-negative and total 1.0 (within a small tolerance). Missing indicators are excluded and the remaining weights are re-normalized; the response reports coverage so missing data is visible.

## Responsible data use

LocalLens AI is informational decision support, not an official neighbourhood grade or a guarantee of safety, air quality, infrastructure, property value, or suitability. Real-world indicator integrations must retain source, collection timestamp, geographic coverage, licensing, and known limitations. Never publish API keys or personal data in the repository.

## Roadmap

1. Backend foundation and scoring validation.
2. PostgreSQL/PostGIS data model and migrations.
3. Source adapters for licensed/open neighbourhood datasets.
4. Routing-provider integration and commute estimates.
5. Comparison persistence and report generation.
6. React + TypeScript application and map interface.
7. Grounded AI explanations with citations to stored source records.
8. Automated tests, security review, deployment, and documentation.
