import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)
RAW_FILE = RAW_DIR / "raw_events.json"
LOG_FILE = RAW_DIR / "ingestion_log.csv"

N_WEEKS = 26
COUNTRY = "GB"
SEGMENT = "Music"

if not API_KEY:
    raise ValueError("API_KEY is not set in environment variables.")


def fetch_window(start_iso: str, end_iso: str, max_pages: int = 5, pause: float = 0.25) -> tuple[list[dict], int]:
    """
    Fetches events from Ticketmaster for a specific date window.
    Returns (events_list, total_reported_elements).
    """
    events = []
    total_elements = 0

    for page in range(max_pages):
        params = {
            "apikey": API_KEY,
            "size": 200,
            "page": page,
            "countryCode": COUNTRY,
            "segmentName": SEGMENT,
            "startDateTime": start_iso,
            "endDateTime": end_iso,
            "sort": "date,asc",
        }

        try:
            response = requests.get(BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            payload = response.json()

            # Extract total elements on first page
            if page == 0:
                total_elements = payload.get("page", {}).get("totalElements", 0)

            batch = payload.get("_embedded", {}).get("events", [])
            if not batch:
                break

            events.extend(batch)

            # Check if all elements retrieved or hit Ticketmaster 1000-deep ceiling
            if len(events) >= total_elements or (page + 1) * 200 >= 1000:
                break

            time.sleep(pause)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching window {start_iso} to {end_iso} (Page {page}): {e}")
            break

    return events, total_elements


def run_ingestion(start_date: datetime | None = None) -> pd.DataFrame:
    """
    Iterates across weekly windows, fetches raw events, saves the combined
    JSON dataset, and outputs an ingestion log DataFrame.
    """
    if start_date is None:
        start_date = datetime.now()

    all_events = []
    log_records = []

    for i in range(N_WEEKS):
        window_start = start_date + timedelta(days=7 * i)
        window_end = window_start + timedelta(days=7)

        start_iso = window_start.strftime("%Y-%m-%dT00:00:00Z")
        end_iso = window_end.strftime("%Y-%m-%dT23:59:59Z")

        print(f"Fetching week {i + 1}/{N_WEEKS}: {start_iso[:10]} to {end_iso[:10]}...")

        fetched_events, total_reported = fetch_window(start_iso, end_iso)
        all_events.extend(fetched_events)

        log_records.append({
            "week_start": window_start.strftime("%Y-%m-%d"),
            "retrieved": len(fetched_events),
            "reported": total_reported,
            "truncated": total_reported > len(fetched_events),
        })

    # Save raw JSON payload locally
    with open(RAW_FILE, "w") as f:
        json.dump(all_events, f, indent=2)
    print(f"\nSaved {len(all_events)} total raw records to {RAW_FILE}")

    # Save the log dataframe
    log_df = pd.DataFrame(log_records)
    log_df.to_csv(LOG_FILE, index=False)
    print(f"Saved ingestion log to {LOG_FILE}")

    return log_df


if __name__ == "__main__":
    run_ingestion()
