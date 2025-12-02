# backend/app.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from backend.predictor import predict_matchup

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    home_team: str
    away_team: str
    season: int
    week: int | None = None
    model_type: str = "linear"  # "linear", "gboost", or "rf"
    neutral_field: bool = False

    @field_validator("season")
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


@app.get("/")
def root():
    return {"status": "ok", "message": "ScoreBot backend running"}


@app.post("/predict")
def predict(req: PredictRequest):
    try:
        result = predict_matchup(
            req.season,
            req.home_team,
            req.away_team,
            req.model_type,
            req.neutral_field
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result
