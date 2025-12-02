import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
import joblib

DATA_DIR = Path("../data")
TEAM_STATS_PATH = DATA_DIR / "team_stats.csv"
GAMES_PATH = DATA_DIR / "games.csv"
MERGED_PATH = DATA_DIR / "merged_dataset.csv"

MODEL_DIR = Path("../models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def merge_dataset() -> pd.DataFrame:
    team_stats = pd.read_csv(TEAM_STATS_PATH)
    games = pd.read_csv(GAMES_PATH)

    # home merge
    ts_home = team_stats.rename(
        columns=lambda c: c if c in ("season", "team") else f"{c}_home"
    )
    merged = games.merge(
        ts_home,
        left_on=["season", "home_team"],
        right_on=["season", "team"],
        how="left",
    )
    merged.drop(columns=["team"], inplace=True)

    # away merge
    ts_away = team_stats.rename(
        columns=lambda c: c if c in ("season", "team") else f"{c}_away"
    )
    merged = merged.merge(
        ts_away,
        left_on=["season", "away_team"],
        right_on=["season", "team"],
        how="left",
    )
    merged.drop(columns=["team"], inplace=True)

    merged = merged.dropna(subset=["home_score", "away_score"])
    merged["home_win"] = (merged["home_score"] > merged["away_score"]).astype(int)
    merged["point_diff"] = merged["home_score"] - merged["away_score"]

    merged.to_csv(MERGED_PATH, index=False)
    print(f"Saved merged dataset to {MERGED_PATH}")
    return merged


def build_feature_matrix(df: pd.DataFrame):
    feature_cols = [
        c
        for c in df.columns
        if (c.endswith("_home") or c.endswith("_away"))
        and pd.api.types.is_numeric_dtype(df[c])
    ]

    X = df[feature_cols]
    y_win = df["home_win"]
    y_diff = df["point_diff"]

    return X, y_win, y_diff, feature_cols


def train_models():
    print("Merging raw data into dataset...")
    df = merge_dataset()

    print("Building feature matrix...")
    X, y_win, y_diff, feature_cols = build_feature_matrix(df)

    X_train_w, X_test_w, y_train_w, y_test_w = train_test_split(
        X, y_win, test_size=0.2, shuffle=True, random_state=42
    )
    X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(
        X, y_diff, test_size=0.2, shuffle=True, random_state=42
    )

    # linear models (speed / baseline)
    linear_win = Pipeline(
        [
            ("impute", SimpleImputer(strategy="mean")),
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=2000)),
        ]
    )
    linear_diff = Pipeline(
        [
            ("impute", SimpleImputer(strategy="mean")),
            ("scale", StandardScaler()),
            ("model", LinearRegression()),
        ]
    )

    print("Training LINEAR logistic regression (home win)...")
    linear_win.fit(X_train_w, y_train_w)
    win_acc_linear = linear_win.score(X_test_w, y_test_w)
    print(f"[LINEAR] Winner accuracy: {win_acc_linear:.4f}")

    print("Training LINEAR regression (point diff)...")
    linear_diff.fit(X_train_d, y_train_d)
    diff_r2_linear = linear_diff.score(X_test_d, y_test_d)
    print(f"[LINEAR] Diff R^2: {diff_r2_linear:.4f}")

    # lightgbm models (gradient boosting / betting)
    lgbm_win = Pipeline(
        [
            ("impute", SimpleImputer(strategy="mean")),
            ("model", LGBMClassifier(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=-1,
                subsample=0.9,
                colsample_bytree=0.9,
                random_state=42,
            )),
        ]
    )
    lgbm_diff = Pipeline(
        [
            ("impute", SimpleImputer(strategy="mean")),
            ("model", LGBMRegressor(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=-1,
                subsample=0.9,
                colsample_bytree=0.9,
                random_state=42,
            )),
        ]
    )

    print("Training LIGHTGBM classifier (home win)...")
    lgbm_win.fit(X_train_w, y_train_w)
    win_acc_lgbm = lgbm_win.score(X_test_w, y_test_w)
    print(f"[LGBM] Winner accuracy: {win_acc_lgbm:.4f}")

    print("Training LIGHTGBM regressor (point diff)...")
    lgbm_diff.fit(X_train_d, y_train_d)
    diff_r2_lgbm = lgbm_diff.score(X_test_d, y_test_d)
    print(f"[LGBM] Diff R^2: {diff_r2_lgbm:.4f}")

    # random forest models (general)
    rf_win = Pipeline(
        [
            ("impute", SimpleImputer(strategy="mean")),
            ("model", RandomForestClassifier(
                n_estimators=400,
                max_depth=None,
                min_samples_split=4,
                min_samples_leaf=2,
                n_jobs=-1,
                random_state=42,
            )),
        ]
    )
    rf_diff = Pipeline(
        [
            ("impute", SimpleImputer(strategy="mean")),
            ("model", RandomForestRegressor(
                n_estimators=400,
                max_depth=None,
                min_samples_split=4,
                min_samples_leaf=2,
                n_jobs=-1,
                random_state=42,
            )),
        ]
    )

    print("Training RANDOM FOREST classifier (home win)...")
    rf_win.fit(X_train_w, y_train_w)
    win_acc_rf = rf_win.score(X_test_w, y_test_w)
    print(f"[RF] Winner accuracy: {win_acc_rf:.4f}")

    print("Training RANDOM FOREST regressor (point diff)...")
    rf_diff.fit(X_train_d, y_train_d)
    diff_r2_rf = rf_diff.score(X_test_d, y_test_d)
    print(f"[RF] Diff R^2: {diff_r2_rf:.4f}")

    # save models & feature metadata
    joblib.dump(linear_win, MODEL_DIR / "linear_win.pkl")
    joblib.dump(linear_diff, MODEL_DIR / "linear_diff.pkl")
    joblib.dump(lgbm_win, MODEL_DIR / "lgbm_win.pkl")
    joblib.dump(lgbm_diff, MODEL_DIR / "lgbm_diff.pkl")
    joblib.dump(rf_win, MODEL_DIR / "rf_win.pkl")
    joblib.dump(rf_diff, MODEL_DIR / "rf_diff.pkl")
    joblib.dump(feature_cols, MODEL_DIR / "feature_cols.pkl")

    print("Saved models and feature metadata.")


if __name__ == "__main__":
    train_models()
