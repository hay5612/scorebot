import pandas as pd
import joblib
import os

DATA_PATH = "data/team_stats.csv"     # aggregated stats per team per season
GAMES_PATH = "data/games.csv"         # optional if needed later

# Load ML models
linear_model = joblib.load("models/linear_model.pkl")
gboost_model = joblib.load("models/gboost_model.pkl")
rf_model = joblib.load("models/rf_model.pkl")


def load_data():
    if not os.path.exists(DATA_PATH):
        raise ValueError("team_stats.csv not found on server.")
    df = pd.read_csv(DATA_PATH)
    return df


def compute_team_features(df, team):
    """
    Aggregate statistics for a team across a season range.
    """
    subset = df[df["team"] == team]

    if subset.empty:
        return None

    # average across selected seasons
    stats = subset.mean(numeric_only=True).to_dict()
    return stats


def build_feature_vector(home_stats, away_stats, neutral_site):
    """
    Construct a single-row DataFrame for model prediction.
    """

    row = {}

    for key, value in home_stats.items():
        row[f"home_{key}"] = value

    for key, value in away_stats.items():
        row[f"away_{key}"] = value

    row["neutral_site"] = int(neutral_site)

    return pd.DataFrame([row])


def predict_matchup(start_season, end_season, home_team, away_team, model_type, neutral_site):
    df = load_data()

    # Slice by season range
    df_range = df[(df["season"] >= start_season) & (df["season"] <= end_season)]
    if df_range.empty:
        raise ValueError("No data available for selected season range.")

    # Build features
    home_stats = compute_team_features(df_range, home_team)
    away_stats = compute_team_features(df_range, away_team)

    if home_stats is None:
        raise ValueError(f"No stats found for home team: {home_team}")
    if away_stats is None:
        raise ValueError(f"No stats found for away team: {away_team}")

    X = build_feature_vector(home_stats, away_stats, neutral_site)

    model_map = {
        "linear": linear_model,
        "gboost": gboost_model,
        "rf": rf_model
    }

    model = model_map.get(model_type)
    if model is None:
        raise ValueError("Invalid model type selected.")

    prediction = model.predict(X)[0]

    winner = home_team if prediction > 0 else away_team
    spread = abs(prediction)

    return {
        "winner": winner,
        "spread": spread,
        "raw_prediction": float(prediction),
        "home_team": home_team,
        "away_team": away_team
    }
