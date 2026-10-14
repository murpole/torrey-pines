"""
Turn the raw downloaded stat tables into one tidy CSV.

WHAT THIS DOES (plain English)
------------------------------
download_pga_stats.py saved one JSON file per (season, tournament, stat), for
example data/raw/pgatour/2024/R2024004/101.json = Driving Distance at the 2024
Farmers Insurance Open. This script:

  1. reads every one of those files,
  2. pulls out one number per player from each (e.g. his average driving distance that week),
  3. lines the five stats up side by side so each row is one player at one event,
  4. adds is_torrey = 1 for the Farmers Insurance Open and 0 for everything else,
  5. saves the result as data/clean/pga_event_stats.csv.

"Tidy" means one row per observation (player x event) and one column per
variable. That's the shape statsmodels and seaborn expect.

It only reads files on your computer; it never goes online.

HOW TO RUN (from the torrey-pines folder, with .venv activated)
--------------------------------------------------------------
  python scripts/build_tidy_csv.py
"""

import json
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw" / "pgatour"
OUT_PATH = PROJECT_DIR / "data" / "clean" / "pga_event_stats.csv"

# Same stat IDs as the download script: stat ID -> our column name.
STATS = {
    "101": "distance",
    "102": "fairway_pct",
    "02675": "sg_total",
    "02674": "sg_t2g",
    "02567": "sg_ott",
}

# Events that aren't normal individual stroke play, so their stats don't mean
# the same thing. We drop them from the analysis.
NOT_STROKE_PLAY = ["zurich", "match play", "presidents cup", "ryder cup"]


def to_number(text):
    """Turn strings like '305.2', '64.29%', '1,234' or '-0.512' into a float.

    Returns None (shown as an empty cell) if there's nothing usable.
    """
    if text is None:
        return None
    cleaned = str(text).replace(",", "").replace("%", "").replace("'", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def main_column(headers):
    """Find which column in a stat table holds the headline number.

    pgatour.com tables have headers like ['AVG.', 'TOTAL DISTANCE', 'TOTAL DRIVES']
    or ['%', 'FAIRWAYS HIT', 'POSSIBLE FAIRWAYS'] or ['AVG', 'TOTAL SG:T', 'MEASURED ROUNDS'].
    The headline number (average, or %) is the one we want. If we can't tell,
    we use the first column.
    """
    for i, h in enumerate(headers):
        if h.strip().upper().rstrip(".") in ("AVG", "AVERAGE", "%"):
            return i
    return 0


def rounds_column(headers):
    """Find the 'measured rounds' column if the table has one (strokes gained tables do)."""
    for i, h in enumerate(headers):
        if "ROUND" in h.upper():
            return i
    return None


def read_one_file(path):
    """Read one saved stat table and return a list of rows (one dict per player)."""
    table = json.loads(path.read_text())
    tournament = table["_tournament"]
    stat_id = path.stem                      # '101.json' -> '101'
    column_name = STATS[stat_id]
    headers = table.get("statHeaders") or []
    value_i = main_column(headers)
    rounds_i = rounds_column(headers)

    rows = []
    for player in table.get("rows") or []:
        if player.get("__typename") != "StatDetailsPlayer":
            continue                         # skip the 'Tour Average' line
        values = [s.get("statValue") for s in player.get("stats") or []]
        row = {
            "player_id": player["playerId"],
            "player": player["playerName"],
            "year": int(path.parent.parent.name),     # the season folder, e.g. '2024'
            "tournament_id": tournament["tournamentId"],
            "event": tournament["displayName"],
            column_name: to_number(values[value_i]) if value_i < len(values) else None,
        }
        if stat_id == "02675" and rounds_i is not None and rounds_i < len(values):
            row["sg_rounds"] = to_number(values[rounds_i])
        rows.append(row)
    return column_name, rows


def build():
    files = sorted(RAW_DIR.glob("*/*/*.json"))   # <year>/<tournament>/<stat>.json
    if not files:
        raise SystemExit(f"No raw files found in {RAW_DIR}. Run download_pga_stats.py first.")

    # Collect a long list of rows for each stat separately.
    by_stat = {name: [] for name in STATS.values()}
    for path in files:
        if path.stem not in STATS:
            continue
        column_name, rows = read_one_file(path)
        by_stat[column_name].extend(rows)

    # Turn each list into a table, then merge the five tables side by side.
    # 'outer' keeps a player-event even if one stat is missing (it shows as empty).
    keys = ["player_id", "player", "year", "tournament_id", "event"]
    tidy = None
    for name, rows in by_stat.items():
        table = pd.DataFrame(rows)
        if table.empty:
            print(f"Warning: no data at all for {name}")
            continue
        tidy = table if tidy is None else tidy.merge(table, on=keys, how="outer")

    # Flag the Farmers Insurance Open (Torrey Pines).
    tidy["is_torrey"] = tidy["event"].str.lower().str.contains("farmers").astype(int)

    # Drop team and match-play events.
    pattern = "|".join(NOT_STROKE_PLAY)
    dropped = tidy["event"].str.lower().str.contains(pattern)
    print(f"Dropping {dropped.sum()} rows from non-stroke-play events: "
          f"{sorted(tidy.loc[dropped, 'event'].unique())}")
    tidy = tidy[~dropped]

    # Put columns in a sensible order and sort.
    order = ["player", "player_id", "year", "event", "tournament_id", "is_torrey",
             "distance", "fairway_pct", "sg_total", "sg_t2g", "sg_ott", "sg_rounds"]
    tidy = tidy[[c for c in order if c in tidy.columns]]
    tidy = tidy.sort_values(["year", "event", "player"]).reset_index(drop=True)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tidy.to_csv(OUT_PATH, index=False)

    # A short report so you can sanity-check the result.
    print(f"\nSaved {len(tidy):,} rows to {OUT_PATH}")
    print(f"Seasons: {tidy['year'].min()}-{tidy['year'].max()}   "
          f"Events: {tidy['tournament_id'].nunique()}   Players: {tidy['player_id'].nunique()}")
    print(f"Torrey rows: {tidy['is_torrey'].sum():,}   Other rows: {(1 - tidy['is_torrey']).sum():,}")
    print("\nMissing values per column:")
    print(tidy.isna().sum().to_string())


if __name__ == "__main__":
    build()
