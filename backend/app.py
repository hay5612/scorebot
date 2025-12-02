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
    start_season: int
    end_season: int
    model_type: str = "linear"   # "linear", "gboost", "rf"
    neutral_site: bool = False

    @field_validator("start_season", "end_season")
    def validate_year(cls, v):
        if v < 2000 or v > 2100:
            raise ValueError("Season must be between 2000 and 2100.")
        return v

    @field_validator("end_season")
    def validate_range(cls, end, info):
        start = info.data.get("start_season")
        if start and end < start:
            raise ValueError("End season cannot be before start season.")
        return end

    @field_validator("model_type")
    def validate_model(cls, v):
        v = v.lower()
        if v not in ("linear", "gboost", "rf"):
            raise ValueError("model_type must be linear, gboost, or rf")
        return v


@app.get("/")
def root():
    return {"status": "ok", "message": "ScoreBot backend running"}


@app.post("/predict")
def predict(req: PredictRequest):
    try:
        result = predict_matchup(
            start_season=req.start_season,
            end_season=req.end_season,
            home_team=req.home_team,
            away_team=req.away_team,
            model_type=req.model_type,
            neutral_site=req.neutral_site
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
