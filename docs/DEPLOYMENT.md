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

## Current user-facing feature coverage

- Explore: search saved catalogue entries, discover additional Indian places through OpenStreetMap, and view known locality-centre markers on an India-wide map.
- Community locality submissions: authenticated users can add descriptions and optional map coordinates; entries remain clearly marked as unverified.
- Compare: select up to three catalogue entries, adjust indicator weights, inspect data coverage/missing indicators, save comparisons to the signed-in account, and export JSON / browser-print PDF.
- Commute: search Indian place names and calculate mapped driving, motorcycle, scooter, cycling or walking routes with a map preview.
- Public transport: open Google Maps Transit for provider-supported bus, metro and train options; fare/ticket resources are links, not an integrated fare engine.
- Ride providers: Uber, Ola, Rapido, inDrive, Namma Yatri and Meru handoffs. Uber attempts to prefill the return locations; other providers require the user to confirm or enter locations.
- Intercity travel: redBus and AbhiBus (buses), IRCTC and ixigo (trains), MakeMyTrip and ixigo (flights), Booking.com and MakeMyTrip (stays).

External provider links are not booking APIs. LocalLens does not fetch provider inventory, compare live prices, issue tickets, or complete payments. Provider availability and categories vary by city.

## Pre-public-launch checklist

- Confirm Supabase Authentication → URL Configuration includes the production frontend URL and allowed redirect URLs.
- Confirm backend `CORS_ORIGINS` includes only the intended production frontend origins.
- Keep only the Supabase publishable/anon key in browser configuration. Never expose service-role keys, database passwords or provider secrets in frontend code or Git.
- Apply and verify every SQL migration in the production Supabase project; test anonymous reads, authenticated inserts and row-level security with separate accounts.
- Add and publish an accurate privacy notice, terms of use, support contact and data-retention process before inviting public users. Explain account email, saved comparisons and community-submitted locality data.
- Add uptime/error monitoring, backup/restore checks, dependency/security scanning and an incident-response owner.
- Test the complete flows on desktop and mobile: catalogue search, OSM discovery, sign-in callback, community submission, saved comparison, export/print, each route profile, transit handoff and ride/travel provider links.
- Replace the free public geocoding, routing and tile endpoints with contracted or self-hosted services before high-volume or business-critical use.
- Replace illustrative indicator values with sourced, dated, licensed and independently reviewed datasets before using scores to make real neighbourhood claims.

## External providers and production readiness

Place search uses OpenStreetMap Nominatim; route estimates use the public Valhalla demo service; maps use OpenStreetMap tiles. These public endpoints have usage policies, rate limits and no production availability guarantee. Do not load-test them or treat them as unrestricted commercial infrastructure. Before a high-traffic public launch, select contracted or self-hosted providers, implement caching/rate limits, and preserve required attribution. The current route profiles are car (`auto`), motorcycle (`motorcycle`, beta), scooter/moped (`motor_scooter`), bicycle (`bicycle`) and walking (`pedestrian`). Public-transport timetables are not configured.

The neighbourhood catalogue contains illustrative sample scores only. Replace them with verified and licensed datasets before presenting real-world assessments. Do not interpret the illustrative index as an official neighbourhood rating.

The Supabase project stores neighbourhoods, indicators and user-scoped saved-comparison records. Row-level security is enabled; anonymous users can read the public catalogue, while saved comparisons are restricted to their authenticated owner. The current UI does not yet expose every database capability.

Before a high-traffic public production launch, replace the community demo geocoder/router/tile infrastructure with providers or self-hosted services that offer an appropriate availability commitment; add caching, rate limiting, monitoring, backups, privacy/terms pages, accessibility review and a security review. Verify the deployed Supabase magic-link redirect allow-list and backend CORS origins. Replace illustrative neighbourhood indicators with verified, licensed, timestamped datasets before presenting factual area ratings. A grounded generative-AI assistant is not part of the current release and would require an approved model provider, API credential, safety evaluation and budget. Build frontend using `npm run build`.
