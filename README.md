# LocalLens AI

**Neighbourhood & Commute Intelligence Platform**

LocalLens AI is a full-stack decision-support application for exploring neighbourhoods, comparing transparent indicators, and estimating journeys between places.

## Current implementation
- React + TypeScript + Vite frontend with responsive dashboard and interactive OpenStreetMap view.
- FastAPI backend with health, neighbourhood catalogue, comparison scoring, place search and commute estimate endpoints.
- Weighted scoring with explicit handling and reporting of missing indicators.
- OpenStreetMap Nominatim place search and OSRM demo route estimates.
- Pytest smoke/scoring tests, Dockerfiles, Docker Compose and GitHub Actions backend test workflow.

**Data warning:** built-in Kharghar, Panvel and Kamothe indicator scores are illustrative demo values, not verified local measurements. Do not use them as factual area ratings.

**Provider warning:** Nominatim, public OSRM demo routing and standard OSM tiles have usage policies and no production availability guarantee. Replace or self-host providers for a public production service, and retain required attribution.

## Run locally

### Backend
```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

### Frontend (second terminal)
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

### Docker
From repository root: `docker compose up --build`.

See [deployment and production checklist](docs/DEPLOYMENT.md).
