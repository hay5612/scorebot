# backend/app.py

from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

# this stays the same – uses your existing predictor
from backend.predictor import predict_matchup

app = FastAPI()

# Allow your static frontend (or any origin) to call this API
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
    week: int
    model_type: Optional[str] = None  # can be null/empty from the UI
    neutral_field: bool = False       # accepted from UI but not used yet

    @field_validator("season")
    @classmethod
    def check_season(cls, v: int) -> int:
        if v < 2000 or v > 2100:
            raise ValueError("Season must be between 2000 and 2100.")
        return v

    @field_validator("week")
    @classmethod
    def check_week(cls, v: int) -> int:
        if v < 1 or v > 22:
            raise ValueError("Week must be between 1 and 22.")
        return v

    @field_validator("model_type")
    @classmethod
    def normalise_model_type(cls, v: Optional[str]) -> str:
        """
        Accepts None or empty as 'default'.
        Also tolerates UI labels like '(default)'.
        """
        if v is None:
            return "default"

        v = v.strip()
        if v == "" or v.lower() in {"(default)", "default"}:
            return "default"

        v = v.lower()
        allowed = {"default", "linear", "gboost", "rf"}
        if v not in allowed:
            raise ValueError(f"model_type must be one of {sorted(allowed)}.")
        return v


@app.get("/")
def root():
    return {"status": "ok", "message": "ScoreBot backend running"}


@app.post("/predict")
def predict(req: PredictRequest):
    """
    Main prediction endpoint.

    Your predictor currently has the signature:
        predict_matchup(start_season, end_season, home_team, away_team, model_type)

    We map the single `season` from the UI to both start_season and end_season.
    `week` and `neutral_field` are accepted from the UI but not yet used here.
    """
    try:
        result = predict_matchup(
            req.season,       # start_season
            req.season,       # end_season
            req.home_team,
            req.away_team,
            req.model_type,   # already normalised/defaulted by validator
        )
    except ValueError as e:
        # Expected data / validation issues
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected errors – don't expose internals
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

    return result
