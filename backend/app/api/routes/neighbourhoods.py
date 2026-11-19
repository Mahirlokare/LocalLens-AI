"""Neighbourhood discovery API."""
from fastapi import APIRouter, HTTPException, Query
from app.data import NEIGHBOURHOODS

router = APIRouter(prefix="/neighbourhoods", tags=["neighbourhoods"])


@router.get("")
def list_neighbourhoods(q: str | None = Query(default=None, max_length=100)):
    """Return the built-in demonstration neighbourhood catalogue."""
    rows = NEIGHBOURHOODS
    if q:
        needle = q.casefold()
        rows = [row for row in rows if needle in row["name"].casefold() or needle in row["city"].casefold()]
    return {"items": rows, "data_status": "illustrative_demo_data",
            "notice": "Demo indicator values are illustrative and must not be used as factual local assessments."}


@router.get("/{neighbourhood_id}")
def get_neighbourhood(neighbourhood_id: str):
    """Fetch a neighbourhood by its stable demo identifier."""
    for row in NEIGHBOURHOODS:
        if row["id"] == neighbourhood_id:
            return row
    raise HTTPException(status_code=404, detail="Neighbourhood not found.")
