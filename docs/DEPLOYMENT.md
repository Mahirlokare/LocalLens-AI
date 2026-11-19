# LocalLens AI — setup and deployment

## Prerequisites
Python 3.11+, Node.js 20+, npm and Git.

## Run API
```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
``
API docs: http://localhost:8000/docs

## Run frontend
In another terminal:
```bash
cd frontend
npm install
# Copy .env.example to .env, then:
npm run dev
``
Open http://localhost:5173.

## Docker
From repository root run `docker compose up --build`.

## External providers and production readiness
Place search uses OpenStreetMap Nominatim; route estimates use the public OSRM demo server; maps use OpenStreetMap tiles. These public endpoints have usage policies, rate limits and no production availability guarantee. Do not load-test them or treat them as unrestricted commercial infrastructure. Before a public launch, select contracted or self-hosted providers, implement caching/rate limits, and preserve required attribution.

The neighbourhood catalogue contains illustrative sample scores only. Replace them with verified and licensed datasets before presenting real-world assessments. Add PostgreSQL/PostGIS persistence, migrations, authentication (if needed), monitoring, HTTPS, secret management, backups, privacy policy, terms, accessibility and security review before production launch. Set exact allowed frontend origins in backend CORS. Build frontend using `npm run build`; deploy `frontend/dist` to a static host and set `VITE_API_URL` at build time.
