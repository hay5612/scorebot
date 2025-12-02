import pandas as pd
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

TEAM_STATS = pd.read_csv(DATA_DIR / "team_stats.csv")

FEATURE_COLS = joblib.load(MODEL_DIR / "feature_cols.pkl")

MODELS = {
    "linear": {
        "win": joblib.load(MODEL_DIR / "linear_win.pkl"),
        "diff": joblib.load(MODEL_DIR / "linear_diff.pkl"),
    },
    "gboost": {
        "win": joblib.load(MODEL_DIR / "lgbm_win.pkl"),
        "diff": joblib.load(MODEL_DIR / "lgbm_diff.pkl"),
    },
    "rf": {
        "win": joblib.load(MODEL_DIR / "rf_win.pkl"),
        "diff": joblib.load(MODEL_DIR / "rf_diff.pkl"),
    },
}


def get_team_stats(team: str, season: int) -> pd.Series:
    team = team.upper().strip()
    subset = TEAM_STATS[(TEAM_STATS["team"] == team) & (TEAM_STATS["season"] == season)]
    if subset.empty:
        raise ValueError(f"No stats found for {team} in season {season}.")
    return subset.iloc[0]


def build_features(season: int, week: int, home_team: str, away_team: str) -> pd.DataFrame:
    home_stats = get_team_stats(home_team, season)
    away_stats = get_team_stats(away_team, season)

    row = {}

    for col, val in home_stats.items():
        if col not in ("team", "season"):
            row[f"{col}_home"] = val

    for col, val in away_stats.items():
        if col not in ("team", "season"):
            row[f"{col}_away"] = val

    df = pd.DataFrame([row])
    df = df.reindex(columns=FEATURE_COLS, fill_value=0)
    return df


def predict_matchup(season: int, week: int, home_team: str, away_team: str,
                    model_type: str = "linear", neutral_field: bool = False):

    model_type = model_type.lower()
    model_win = MODELS[model_type]["win"]
    model_diff = MODELS[model_type]["diff"]

    X = build_features(season, week, home_team, away_team)

    win_prob = float(model_win.predict_proba(X)[0, 1])
    diff = float(model_diff.predict(X)[0])

    if neutral_field:
        diff = diff * 0.9  # small adjustment

    winner = home_team.upper() if diff >= 0 else away_team.upper()

    return {
        "season": season,
        "week": week,
        "home_team": home_team.upper(),
        "away_team": away_team.upper(),
        "model_type": model_type,
        "home_win_probability": win_prob,
        "predicted_point_diff": diff,
        "predicted_winner": winner,
    }
