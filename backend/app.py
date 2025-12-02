# backend/app.py

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, field_validator

from backend.predictor import predict_matchup

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI()

# Allow frontend → backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================
# REQUEST MODEL
# ===========================
class PredictRequest(BaseModel):
    home_team: str
    away_team: str
    season: int
    week: int | None = None
    model_type: str = "linear"
    neutral_field: bool = False

    @field_validator("season")
    def validate_year(cls, v: int):
        if v < 2000 or v > 2100:
            raise ValueError("Season must be between 2000 and 2100.")
        return v

    @field_validator("model_type")
    def validate_model(cls, v: str):
        v = v.lower()
        if v not in ("linear", "gboost", "rf"):
            raise ValueError("model_type must be 'linear', 'gboost', or 'rf'.")
        return v


# ==============================
# SERVE FRONTEND (THE FIX)
# ==============================
@app.get("/", response_class=HTMLResponse)
def serve_index():
    """Serve the prediction UI as the homepage."""
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/script.js")
def serve_js():
    return FileResponse(FRONTEND_DIR / "script.js", media_type="application/javascript")


@app.get("/style.css")
def serve_css():
    return FileResponse(FRONTEND_DIR / "style.css", media_type="text/css")


# ===========================
# HEALTH CHECK (optional)
# ===========================
@app.get("/health")
def health():
    return {"status": "ok", "message": "ScoreBot backend running"}


# ===========================
# PREDICTION API
# ===========================
@app.post("/predict")
def predict(req: PredictRequest):
    try:
        result = predict_matchup(
            req.season,
            req.home_team,
            req.away_team,
            req.model_type,
            req.neutral_field,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
