# backend/app.py

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, field_validator, ConfigDict

from backend.predictor import predict_matchup

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# request model
class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    home_team: str
    away_team: str
    start_season: int
    end_season: int

    model_type: str = "linear"
    neutral_field: bool = False # not used, but accepted

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
            raise ValueError("model_type must be 'linear', 'gboost', or 'rf'")
        return v


# serve frontend
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/style.css")
async def serve_css():
    return FileResponse(FRONTEND_DIR / "style.css")


@app.get("/script.js")
async def serve_js():
    return FileResponse(FRONTEND_DIR / "script.js")


# api
@app.post("/predict")
def predict(req: PredictRequest):

    if req.start_season > req.end_season:
        raise HTTPException(
            status_code=400,
            detail="start_season must be <= end_season."
        )

    try:
        result = predict_matchup(
            req.start_season,
            req.end_season,
            req.home_team,
            req.away_team,
            req.model_type
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result


@app.get("/health")
def health():
    return {"status": "ok"}
