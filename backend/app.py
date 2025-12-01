# backend/app.py

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, field_validator, ConfigDict

from backend.predictor import predict_matchup

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # project root
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI()

# ------------------------------------------------------------------
# CORS (safe even if frontend is same origin)
# ------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # you can tighten this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Request model for /predict
#   Designed to work with both old and new frontends:
#   - supports season OR start_season/end_season
#   - ignores extra fields like week, neutral flag, etc.
# ------------------------------------------------------------------
class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")  # ignore unknown fields

    home_team: str
    away_team: str

    # either a single season...
    season: int | None = None
    # ...or explicit range
    start_season: int | None = None
    end_season: int | None = None

    model_type: str | None = "linear"  # "linear", "gboost", or "rf"
    neutral_field: bool = False

    @field_validator("season", "start_season", "end_season")
    @classmethod
    def check_year(cls, v: int | None) -> int | None:
        if v is None:
            return v
        if v < 2000 or v > 2100:
            raise ValueError("Season must be between 2000 and 2100.")
        return v

    @field_validator("model_type")
    @classmethod
    def check_model_type(cls, v: str | None) -> str:
        if v is None or v == "":
            return "linear"
        v = v.lower()
        if v not in ("linear", "gboost", "rf"):
            raise ValueError("model_type must be 'linear', 'gboost', or 'rf'.")
        return v


# ------------------------------------------------------------------
# Frontend routes: serve the prediction UI at "/"
# ------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the prediction UI as the main page."""
    index_path = FRONTEND_DIR / "index.html"
    return FileResponse(index_path)


@app.get("/style.css")
async def serve_css():
    """Serve the main stylesheet."""
    css_path = FRONTEND_DIR / "style.css"
    return FileResponse(css_path, media_type="text/css")


@app.get("/script.js")
async def serve_js():
    """Serve the frontend JavaScript."""
    js_path = FRONTEND_DIR / "script.js"
    return FileResponse(js_path, media_type="application/javascript")


# Optional: simple JSON health check, if you still want one
@app.get("/health")
def health():
    return {"status": "ok", "message": "ScoreBot backend running"}


# ------------------------------------------------------------------
# API route for predictions
# ------------------------------------------------------------------
@app.post("/predict")
def predict(req: PredictRequest):
    # Support both schemas:
    # - if start/end provided, use them
    # - if only season provided, use it for both
    start = req.start_season or req.season
    end = req.end_season or req.season

    if start is None or end is None:
        raise HTTPException(
            status_code=400,
            detail="You must provide either 'season' or both 'start_season' and 'end_season'.",
        )

    try:
        result = predict_matchup(
            start,
            end,
            req.home_team,
            req.away_team,
            req.model_type or "linear",
        )
    except ValueError as e:
        # For things like unknown team codes, bad year ranges, etc.
        raise HTTPException(status_code=400, detail=str(e))

    return result
