import nfl_data_py as nfl
import pandas as pd
from pathlib import Path

START = 2018
END = 2024

OUT_DIR = Path("../data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def ensure_caches():
    years = list(range(START, END + 1))
    print(f"Caching PBP for {years}...")
    nfl.cache_pbp(years)
    print("PBP caching complete.\n")

def load_data():
    years = list(range(START, END + 1))

    print("Loading play-by-play data...")
    pbp = nfl.import_pbp_data(years)
    pbp = pbp.apply(pd.to_numeric, errors="ignore", downcast="float")

    print("Loading schedules...")
    sched = nfl.import_schedules(years)

    return pbp, sched

def aggregate_team_stats(pbp: pd.DataFrame) -> pd.DataFrame:
    print("Aggregating team-level features...")

    pbp["pass_epa"] = pbp["epa"].where(pbp["play_type"] == "pass")
    pbp["rush_epa"] = pbp["epa"].where(pbp["play_type"] == "run")

    grouped = pbp.groupby(["season", "posteam"]).agg(
        epa=("epa", "mean"),
        pass_epa=("pass_epa", "mean"),
        rush_epa=("rush_epa", "mean"),
        air_epa=("air_epa", "mean"),
        yac_epa=("yac_epa", "mean"),
        comp_air_epa=("comp_air_epa", "mean"),
        comp_yac_epa=("comp_yac_epa", "mean"),
        qb_epa=("qb_epa", "mean"),
        xyac_epa=("xyac_epa", "mean"),
        success=("success", "mean"),
        yards_gained=("yards_gained", "mean"),
        plays=("play_type", "count"),
    ).reset_index()

    grouped.rename(columns={"posteam": "team"}, inplace=True)
    return grouped

def build():
    ensure_caches()
    pbp, sched = load_data()

    team_stats = aggregate_team_stats(pbp)

    print("Saving CSV files...")
    team_stats.to_csv(OUT_DIR / "team_stats.csv", index=False)
    sched.to_csv(OUT_DIR / "games.csv", index=False)
    print("Done.")

if __name__ == "__main__":
    build()
