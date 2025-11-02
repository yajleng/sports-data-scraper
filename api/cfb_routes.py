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

@router.post("/run_model")
def run_model(
    home: str = Query(..., description="Home team name"),
    away: str = Query(..., description="Away team name"),
    year: int = Query(..., description="Season year"),
    week: int = Query(..., description="Week number"),
    validate: bool = Query(default=True, description="Run validation before model"),
):
    """
    Build model inputs, optionally validate, then execute the deterministic
    cfb_spread_model.py and return its predictions.

    Example:
        POST /cfb/run_model?home=Georgia&away=Alabama&year=2025&week=10
    """
    try:
        from subprocess import run
        from pathlib import Path
        import tempfile, json

        # Step 1 — Build inputs using the bridge
        data = cfb_to_model.build_inputs(home, away, year, week)

        if validate:
            ok = cfb_to_model.validate_inputs(data)
            if not ok:
                return JSONResponse(
                    status_code=422,
                    content={"status": "validation_failed", "data": data},
                )

        # Step 2 — Write temporary input file
        tmp_input = Path(tempfile.gettempdir()) / "cfb_input.json"
        tmp_input.write_text(json.dumps(data, indent=2))

        # Step 3 — Run deterministic model
        tmp_output = Path(tempfile.gettempdir()) / "cfb_output.json"
        cmd = ["python", "cfb_spread_model.py", "--input", str(tmp_input), "--out", str(tmp_output)]
        result = run(cmd, capture_output=True, text=True)

        # Handle subprocess output
        if result.returncode != 0:
            raise RuntimeError(f"Model execution failed:\n{result.stderr}")

        if not tmp_output.exists():
            raise FileNotFoundError("Model output file not found after run.")

        output_data = json.loads(tmp_output.read_text())

        return JSONResponse(
            content={
                "status": "ok",
                "model_output": output_data,
                "stderr": result.stderr,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model run failed: {e}")
