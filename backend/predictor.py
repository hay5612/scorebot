# backend/predictor.py

from pathlib import Path
import pandas as pd
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

TEAM_STATS_PATH = DATA_DIR / "team_stats.csv"
FEATURE_COLS_PATH = MODEL_DIR / "feature_cols.pkl"

MODEL_FILES = {
    "linear": {
        "win": MODEL_DIR / "linear_win.pkl",
        "diff": MODEL_DIR / "linear_diff.pkl",
    },
    "gboost": {
        "win": MODEL_DIR / "lgbm_win.pkl",
        "diff": MODEL_DIR / "lgbm_diff.pkl",
    },
    "rf": {
        "win": MODEL_DIR / "rf_win.pkl",
        "diff": MODEL_DIR / "rf_diff.pkl",
    },
}

_team_stats = pd.read_csv(TEAM_STATS_PATH)
_feature_cols = joblib.load(FEATURE_COLS_PATH)
_MODEL_CACHE = {}


def _normalize_team(code: str) -> str:
    return code.strip().upper()


def _load_models(model_type: str):
    model_type = model_type.lower()

    if model_type not in MODEL_FILES:
        raise ValueError("Unknown model_type: must be linear, gboost, or rf")

    if model_type in _MODEL_CACHE:
        return

    files = MODEL_FILES[model_type]
    _MODEL_CACHE[model_type] = {
        "win": joblib.load(files["win"]),
        "diff": joblib.load(files["diff"]),
    }


def _aggregate_team_stats(team: str, season: int):
    team = _normalize_team(team)
    subset = _team_stats[
        (_team_stats["team"] == team) & (_team_stats["season"] == season)
    ]

    if subset.empty:
        raise ValueError(f"No stats found for team {team} in season {season}")

    numeric_cols = subset.select_dtypes(include="number")
    return numeric_cols.mean()


def _build_feature_row(season: int, home_team: str, away_team: str):
    home_stats = _aggregate_team_stats(home_team, season)
    away_stats = _aggregate_team_stats(away_team, season)

    row = {}

    for col, val in home_stats.items():
        if col != "season":
            row[f"{col}_home"] = val

    for col, val in away_stats.items():
        if col != "season":
            row[f"{col}_away"] = val

    df = pd.DataFrame([row])
    df = df.reindex(columns=_feature_cols, fill_value=0.0)

    return df


def predict_matchup(season: int, home_team: str, away_team: str,
                    model_type: str, neutral_field: bool = False):

    _load_models(model_type)

    models = _MODEL_CACHE[model_type]

    X = _build_feature_row(season, home_team, away_team)

    win_model = models["win"]
    diff_model = models["diff"]

    win_prob = float(win_model.predict_proba(X)[0][1])
    point_diff = float(diff_model.predict(X)[0])

    if neutral_field:
        point_diff *= 0.9

    winner = (
        _normalize_team(home_team)
        if point_diff >= 0
        else _normalize_team(away_team)
    )

    return {
        "season": season,
        "home_team": _normalize_team(home_team),
        "away_team": _normalize_team(away_team),
        "home_win_probability": win_prob,
        "predicted_point_diff": point_diff,
        "predicted_winner": winner
    }
