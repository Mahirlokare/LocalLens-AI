# LocalLens AI — API Reference

Base URL (production): `https://locallens-ai-api-1sgb.onrender.com`

Interactive OpenAPI documentation: [`/docs`](https://locallens-ai-api-1sgb.onrender.com/docs)

All application endpoints use the `/v1` prefix unless noted. JSON request bodies and responses use UTF-8.

## Endpoint index

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health check |
| GET | `/v1/neighbourhoods` | List the built-in demo locality catalogue |
| GET | `/v1/neighbourhoods/{neighbourhood_id}` | Fetch one demo locality by ID |
| GET | `/v1/places/suggest?q={query}` | Interactive place suggestions (Photon, with fallback) |
| GET | `/v1/places/search?q={query}` | Explicit India place search |
| POST | `/v1/commute/estimate` | Calculate a mapped route |
| POST | `/v1/comparisons/score` | Calculate weighted locality scores |

## 1. Health

`GET /health`

Example response:

```json
{ "status": "ok", "service": "locallens-api" }
```

## 2. Neighbourhood catalogue

`GET /v1/neighbourhoods`

Optional query parameter: `q` (maximum 100 characters), filters by locality name or city.

`GET /v1/neighbourhoods/{neighbourhood_id}`

Returns a single built-in demo entry or HTTP 404. The built-in catalogue and its illustrative indicators are not a verified nationwide dataset.

## 3. Place discovery

`GET /v1/places/suggest?q=Kharghar%2C%20India`

Returns up to six suggestion records. Photon is the primary suggestion provider; Open-Meteo geocoding is a fallback.

`GET /v1/places/search?q=Kharghar%2C%20Navi%20Mumbai`

Returns up to eight place results. Photon is tried first, followed by Nominatim and Open-Meteo fallback.

Both endpoints require a query between 2 and 180 characters and return an array with:

- `display_name`
- `latitude`
- `longitude`
- `category` (optional)

Provider availability, coverage and fair-use limits apply.

## 4. Commute estimate

`POST /v1/commute/estimate`

Example request:

```json
{
  "origin_lat": 19.0473,
  "origin_lon": 73.0699,
  "destination_lat": 18.9398,
  "destination_lon": 72.8355,
  "mode": "driving"
}
```

Supported `mode` values: `driving`, `motorcycle`, `scooter`, `cycling`, `walking`.

Coordinates are validated against latitude and longitude ranges. The response includes `distance_km`, `duration_minutes`, `mode`, route `geometry`, `provider` and a `disclaimer`.

Routes use Valhalla and OpenStreetMap mapped networks. They are estimates, not live-traffic predictions. Public transport is an external Google Maps Transit handoff in the frontend; it is not a native backend route mode.

## 5. Weighted comparison

`POST /v1/comparisons/score`

**Selection limits:** each request must contain at least two and at most three distinct localities. The backend enforces this even if a client bypasses the interface.

Example request:

```json
{
  "weights": {
    "healthcare": 0.25,
    "transit": 0.25,
    "education": 0.25,
    "environment": 0.25
  },
  "neighbourhoods": [
    {
      "name": "Area A",
      "indicators": {
        "healthcare": {
          "value": 80,
          "source": "Example public dataset",
          "observed_at": "2026-11-01"
        }
      }
    },
    {
      "name": "Area B",
      "indicators": {
        "transit": {
          "value": 65,
          "source": "Example public dataset",
          "observed_at": "2026-11-01"
        }
      }
    }
  ]
}
```

Validation rules:

- Each locality name must be non-empty and no longer than 120 characters.
- Locality names must be unique (case-insensitive).
- Each request contains 2–3 localities.
- Indicator values must be between 0 and 100.
- Every indicator must include a source (1–300 characters) and observation date/text (1–64 characters).
- Weights must be non-negative, contain at least one entry, and sum to 1.0 (within a small floating-point tolerance).

The response returns a score, data coverage, missing indicators and indicator-level breakdown for each locality, plus methodology and a disclaimer. Missing indicators are excluded and available weights are re-normalized; a locality with no supplied indicators has zero coverage and should be shown as unrated.

## Error handling

- `200`: request completed.
- `404`: requested demo locality was not found.
- `422`: invalid query, coordinates, travel mode or request body.
- `502`: a place or routing provider is temporarily unavailable.

## Authentication and database note

The REST endpoints documented above do not implement user-session authentication. The frontend uses Supabase Auth and the Supabase client directly for sign-in, community locality submissions and saved comparisons; access to protected database rows is governed by Supabase Row Level Security. Email magic-link delivery depends on the Supabase Auth email/SMTP configuration and production redirect allow-list.
