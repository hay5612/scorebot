from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

from backend.predictor import predict_matchup


app = FastAPI()

# CORS so you can hit this from any frontend (or directly in the browser)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten later if you want
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    home_team: str
    away_team: str
    start_season: int
    end_season: int
    model_type: str = "linear"  # "linear", "gboost", or "rf"

    @field_validator("start_season", "end_season")
    @classmethod
    def check_year(cls, v: int) -> int:
        if v < 2000 or v > 2100:
            raise ValueError("Season must be between 2000 and 2100.")
        return v

    @field_validator("model_type")
    @classmethod
    def check_model_type(cls, v: str) -> str:
        v = v.lower()
        if v not in ("linear", "gboost", "rf"):
            raise ValueError("model_type must be 'linear', 'gboost', or 'rf'.")
        return v


# Health check / status endpoint (JSON)
@app.get("/api/health")
def health():
    return {"status": "ok", "message": "ScoreBot backend running"}


# Prediction endpoint used by the UI
@app.post("/predict")
def predict(req: PredictRequest):
    try:
        result = predict_matchup(
            req.start_season,
            req.end_season,
            req.home_team,
            req.away_team,
            req.model_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


# Serve the frontend (index.html, script.js, style.css) from the "frontend" folder.
# Make sure you have: frontend/index.html, frontend/script.js, frontend/style.css
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
