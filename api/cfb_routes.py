# api/cfb_routes.py
"""
FastAPI router exposing endpoints for college football input generation.
Allows external callers (like your GPT or backend) to build and validate
model-ready JSON via HTTP.
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from bridges import cfb_to_model

router = APIRouter(prefix="/cfb", tags=["College Football"])


@router.get("/build_inputs")
def build_inputs(
    home: str = Query(..., description="Home team name"),
    away: str = Query(..., description="Away team name"),
    year: int = Query(..., description="Season year"),
    week: int = Query(..., description="Week number"),
    validate: bool = Query(default=True, description="Run validation before returning")
):
    """
    Build model-ready JSON inputs using your data scrapers.
    Example call:
        GET /cfb/build_inputs?home=Georgia&away=Alabama&year=2025&week=10
    """
    try:
        data = cfb_to_model.build_inputs(home, away, year, week)

        if validate:
            ok = cfb_to_model.validate_inputs(data)
            if not ok:
                return JSONResponse(
                    status_code=422,
                    content={"status": "validation_failed", "data": data},
                )

        return JSONResponse(content={"status": "ok", "data": data})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build inputs: {e}")
