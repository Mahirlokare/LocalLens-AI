# LocalLens AI — setup and deployment

## Live deployment (free tier)

- Frontend: https://locallens-ai-frontend.onrender.com
- Backend API: https://locallens-ai-api-1sgb.onrender.com
- Health check: https://locallens-ai-api-1sgb.onrender.com/health
- Interactive API documentation: https://locallens-ai-api-1sgb.onrender.com/docs

The frontend is a Render Static Site and the API is a Render Free Web Service. The API may spin down after inactivity on the free tier and take time to wake up. No paid Render plan is configured.

## Prerequisites

Python 3.11+, Node.js 20+, npm and Git.

## Run the API locally

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## Run the frontend locally

In another terminal:

```bash
cd frontend
npm install
# Copy .env.example to .env, then:
npm run dev
```

Open http://localhost:5173.

## Docker

From repository root run `docker compose up --build`.

## External providers and production readiness

Place search uses OpenStreetMap Nominatim; route estimates use the public OSRM demo server; maps use OpenStreetMap tiles. These public endpoints have usage policies, rate limits and no production availability guarantee. Do not load-test them or treat them as unrestricted commercial infrastructure. Before a high-traffic public launch, select contracted or self-hosted providers, implement caching/rate limits, and preserve required attribution.

The neighbourhood catalogue contains illustrative sample scores only. Replace them with verified and licensed datasets before presenting real-world assessments. Do not interpret the illustrative index as an official neighbourhood rating.

The Supabase project stores neighbourhoods, indicators and user-scoped saved-comparison records. Row-level security is enabled; anonymous users can read the public catalogue, while saved comparisons are restricted to their authenticated owner. The current UI does not yet expose every database capability.

Before a production-grade public launch, complete authentication and saved-comparison UI, downloadable reports, a grounded generative-AI assistant (which requires an explicitly configured model provider and API credential), source-verified neighbourhood metrics, privacy/terms pages, monitoring, backups, accessibility and security review. Set exact allowed frontend origins in backend CORS. Build frontend using `npm run build`.
