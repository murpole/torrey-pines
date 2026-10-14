"""
Download per-event PGA TOUR stats from pgatour.com's data feed.

WHAT THIS DOES (plain English)
------------------------------
pgatour.com's stats pages are filled in by a "GraphQL" data feed: your browser
sends a small question ("give me Driving Distance for the 2024 Farmers
Insurance Open, that event only") and gets back a table as JSON text. This
script asks the same questions your browser would, one at a time, and saves
each answer to a file in data/raw/pgatour/.

It is polite and safe to re-run:
  * It waits at least 1 second between requests.
  * It never asks twice: if a file is already saved, it is skipped. If the
    run stops halfway (Wi-Fi drops, laptop sleeps), just run it again.
  * It saves the answers exactly as received. Cleaning happens later, in
    build_tidy_csv.py, so the raw data is never edited.

NOTE: PGA TOUR's Terms of Use (section 7(C)) forbid downloading stats with
scripts. You chose this route knowingly; the data is for a personal,
non-commercial portfolio project. See notes/step2-data-sources.md.

HOW TO RUN (from the torrey-pines folder, with .venv activated)
--------------------------------------------------------------
  python scripts/download_pga_stats.py --probe        # 1 test request, prints what came back
  python scripts/download_pga_stats.py --torrey-only  # just the Farmers Insurance Open, all years
  python scripts/download_pga_stats.py                # every event, 2017-2026 (~2,000 requests, ~40 min)
"""

import argparse   # reads options like --probe from the command line
import json       # converts between JSON text and Python dictionaries
import os         # reads environment variables (for an optional API key override)
import sys        # lets us exit with an error message
import time       # for waiting between requests
from pathlib import Path  # a convenient way to build file paths

import requests   # sends web requests

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

# The address pgatour.com's pages send their data questions to.
GRAPHQL_URL = "https://orchestrator.pgatour.com/graphql"

# pgatour.com's pages include this public key in every request. It is not a
# password and not tied to you. It can change; if requests start failing with
# 401/403, see the message printed by the script for how to find the new one.
API_KEY = os.environ.get("PGA_API_KEY", "da2-gsrx5bibzbb4njvhl7t37wqyl4")

# The five stats we want, by pgatour.com's stat ID -> our short column name.
STATS = {
    "101": "distance",       # Driving Distance (yards, measured drives)
    "102": "fairway_pct",    # Driving Accuracy Percentage
    "02675": "sg_total",     # Strokes Gained: Total
    "02674": "sg_t2g",       # Strokes Gained: Tee-to-Green
    "02567": "sg_ott",       # Strokes Gained: Off-the-Tee
}

YEARS = range(2017, 2027)    # 2017, 2018, ..., 2026 (range stops before 2027)
SECONDS_BETWEEN_REQUESTS = 1.0

# Folder where raw answers are saved: data/raw/pgatour/<year>/...
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw" / "pgatour"

# The GraphQL "question". It asks for one stat table: the table's title, the
# column headers, the list of tournaments that season ("tournamentPills"),
# and one row per player.
STAT_QUERY = """
query StatDetails($tourCode: TourCode!, $statId: String!, $year: Int, $eventQuery: StatDetailEventQuery) {
  statDetails(tourCode: $tourCode, statId: $statId, year: $year, eventQuery: $eventQuery) {
    year
    displaySeason
    statId
    statTitle
    tourAvg
    statHeaders
    tournamentPills { tournamentId displayName }
    rows {
      ... on StatDetailsPlayer {
        __typename
        playerId
        playerName
        rank
        stats { statName statValue }
      }
    }
  }
}
"""

# ---------------------------------------------------------------------------
# Talking to the server
# ---------------------------------------------------------------------------

_last_request_time = 0.0


def ask_pgatour(variables):
    """Send one question to pgatour.com and return the answer as a dictionary.

    Waits so requests are at least 1 second apart, and retries a few times if
    the server is busy (HTTP 429) or has a hiccup (HTTP 5xx).
    """
    global _last_request_time
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
        "x-pgat-platform": "web",
        "Origin": "https://www.pgatour.com",
        "Referer": "https://www.pgatour.com/",
        "User-Agent": "torrey-pines-student-project (personal, non-commercial)",
    }
    body = {"operationName": "StatDetails", "query": STAT_QUERY, "variables": variables}

    for attempt in range(1, 5):
        # Wait until at least SECONDS_BETWEEN_REQUESTS have passed since the last request.
        wait = SECONDS_BETWEEN_REQUESTS - (time.time() - _last_request_time)
        if wait > 0:
            time.sleep(wait)
        _last_request_time = time.time()

        response = requests.post(GRAPHQL_URL, json=body, headers=headers, timeout=30)

        if response.status_code in (401, 403):
            sys.exit(
                f"\nThe server refused the request (HTTP {response.status_code}). The public key has\n"
                "probably changed. To find the new one: open https://www.pgatour.com/stats in Chrome,\n"
                "press Cmd+Option+I, go to the Network tab, reload, click any 'graphql' request and\n"
                "copy the 'x-api-key' value under Request Headers. Then run:\n"
                "    export PGA_API_KEY=<the new key>\n"
                "and run this script again."
            )
        if response.status_code == 429 or response.status_code >= 500:
            pause = 5 * attempt
            print(f"   server busy (HTTP {response.status_code}), waiting {pause}s and retrying...")
            time.sleep(pause)
            continue

        response.raise_for_status()   # stop with an error for any other bad status
        answer = response.json()
        if answer.get("errors"):
            # GraphQL reports problems inside the answer rather than as an HTTP error.
            raise RuntimeError(json.dumps(answer["errors"], indent=2))
        return answer["data"]["statDetails"]

    raise RuntimeError("Gave up after 4 attempts.")


def event_only(tournament_id):
    """The filter that means 'this one tournament only' (pgatour.com's 'Tournament Only' view)."""
    return {"queryType": "EVENT_ONLY", "tournamentId": tournament_id}


# ---------------------------------------------------------------------------
# Saving and loading
# ---------------------------------------------------------------------------

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)   # create folders if needed
    path.write_text(json.dumps(data, indent=1))


def get_tournament_list(year):
    """Return the season's tournaments as a list of {tournamentId, displayName}.

    pgatour.com includes this list with every stat table, so we ask for the
    season-long Driving Distance table once per year and keep the list.
    """
    path = RAW_DIR / str(year) / "tournaments.json"
    if path.exists():
        return json.loads(path.read_text())
    table = ask_pgatour({"tourCode": "R", "statId": "101", "year": year, "eventQuery": None})
    tournaments = table.get("tournamentPills") or []
    save_json(path, tournaments)
    return tournaments


def is_farmers(tournament):
    return "farmers" in tournament["displayName"].lower()


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def probe():
    """Make one request for the most recent Farmers and print what came back."""
    for year in sorted(YEARS, reverse=True):
        tournaments = get_tournament_list(year)
        farmers = [t for t in tournaments if is_farmers(t)]
        if farmers:
            break
    else:
        sys.exit("Couldn't find the Farmers Insurance Open in any season's tournament list.")

    t = farmers[0]
    print(f"Found {len(tournaments)} tournaments in {year}. Farmers = {t}")
    table = ask_pgatour({"tourCode": "R", "statId": "101", "year": year,
                         "eventQuery": event_only(t["tournamentId"])})
    rows = [r for r in table["rows"] if r.get("__typename") == "StatDetailsPlayer"]
    print(f"Title: {table['statTitle']}   Headers: {table['statHeaders']}")
    print(f"Players in table: {len(rows)}   Tour average shown: {table['tourAvg']}")
    for r in rows[:5]:
        print("  ", r["playerName"], [s["statValue"] for s in r["stats"]])
    print("\nIf the player count looks like one tournament's field (roughly 70-160 players,\n"
          "not ~190 for a whole season), the event-only filter works. Paste this output in the thread.")


def download(torrey_only):
    total_saved = 0
    errors_in_a_row = 0
    for year in YEARS:
        tournaments = get_tournament_list(year)
        if torrey_only:
            tournaments = [t for t in tournaments if is_farmers(t)]
        print(f"{year}: {len(tournaments)} tournaments")

        for t in tournaments:
            tid = t["tournamentId"]
            for stat_id, name in STATS.items():
                path = RAW_DIR / str(year) / tid / f"{stat_id}.json"
                if path.exists():
                    continue   # already downloaded on an earlier run
                try:
                    table = ask_pgatour({"tourCode": "R", "statId": stat_id, "year": year,
                                         "eventQuery": event_only(tid)})
                except RuntimeError as err:
                    # Some events (team events, match play) have no table for some stats.
                    # We don't save anything, so a later run will try again.
                    print(f"   skipped {t['displayName']} / {name}: {str(err)[:120]}")
                    errors_in_a_row += 1
                    if errors_in_a_row >= 5:
                        sys.exit("\n5 errors in a row, so something is wrong with the request "
                                 "itself. Stopping. Paste the messages above in the thread.")
                    continue
                errors_in_a_row = 0
                table["_tournament"] = t   # remember which event this file is for
                save_json(path, table)
                total_saved += 1
            print(f"   done: {t['displayName']}")
    print(f"\nFinished. Saved {total_saved} new files under {RAW_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download per-event PGA TOUR stats.")
    parser.add_argument("--probe", action="store_true", help="make one test request and print it")
    parser.add_argument("--torrey-only", action="store_true", help="only the Farmers Insurance Open")
    args = parser.parse_args()

    if args.probe:
        probe()
    else:
        download(torrey_only=args.torrey_only)
