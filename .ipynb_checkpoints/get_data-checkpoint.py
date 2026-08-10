"""Ticketmaster ingestion. Writes data/processed/clean_events.csv for the app.

The output schema is what Home.py and the pages expect; changing a column name
here breaks bases() and the page charts.
"""
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

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

RAW_FILE = RAW_DIR / "raw_events.json"
LOG_FILE = PROCESSED_DIR / "ingestion_log.csv"
CLEAN_FILE = PROCESSED_DIR / "clean_events.csv"

N_WEEKS = 26
COUNTRY = "GB"
SEGMENT = "Music"

if not API_KEY:
    raise ValueError("API_KEY is not set in environment variables.")


def fetch_window(start_iso: str, end_iso: str, max_pages: int = 5,
                 pause: float = 0.25) -> tuple[list[dict], int]:
    """Fetch one date window. Returns (events, total_reported_elements)."""
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

            if page == 0:
                total_elements = payload.get("page", {}).get("totalElements", 0)

            batch = payload.get("_embedded", {}).get("events", [])
            if not batch:
                break

            events.extend(batch)

            # Stop at the end of the results or Ticketmaster's 1000-record ceiling.
            if len(events) >= total_elements or (page + 1) * 200 >= 1000:
                break

            time.sleep(pause)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching window {start_iso} to {end_iso} (page {page}): {e}")
            break

    return events, total_elements


def _first(items, *keys):
    """Read a nested key off the first element of a list, tolerating gaps."""
    if not items:
        return None
    node = items[0]
    for k in keys:
        if not isinstance(node, dict):
            return None
        node = node.get(k)
    return node


def parse_and_clean(raw_events: list[dict], fetched_at: str) -> pd.DataFrame:
    """Flatten to the schema the dashboard reads."""
    records = []

    for event in raw_events:
        venues = event.get("_embedded", {}).get("venues") or []
        attractions = event.get("_embedded", {}).get("attractions") or []
        classifications = event.get("classifications") or []
        prices = event.get("priceRanges") or []

        records.append({
            "id": event.get("id"),
            "name": event.get("name"),
            "genre": _first(classifications, "genre", "name"),
            "subgenre": _first(classifications, "subGenre", "name"),
            "city": _first(venues, "city", "name"),
            "venue_id": _first(venues, "id"),
            "venue_name": _first(venues, "name"),
            "latitude": _first(venues, "location", "latitude"),
            "longitude": _first(venues, "location", "longitude"),
            "attraction_id": _first(attractions, "id"),
            "attraction_name": _first(attractions, "name"),
            "event_date": event.get("dates", {}).get("start", {}).get("localDate"),
            # Retained deliberately: these stay null on public API keys, which is
            # itself the evidence for the no-pricing caveat.
            "min_price": _first(prices, "min"),
            "max_price": _first(prices, "max"),
            "currency": _first(prices, "currency"),
            "url": event.get("url"),
        })

    df = pd.DataFrame(records).drop_duplicates(subset="id").reset_index(drop=True)

    # Coordinates arrive as strings; cast so Tableau reads them as geographic.
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")

    # Some venues append a postcode to the city field ("Newcastle Upon Tyne,
    # NE1 2PQ"), splitting one city across two buckets.
    text = ["genre", "subgenre", "city", "attraction_name"]
    df[text] = df[text].apply(lambda s: s.str.strip()).replace("Undefined", pd.NA)
    df["city"] = df["city"].str.split(",").str[0].str.strip().str.title()

    # Stamped once per ingestion so every row shares a timestamp — Home.py reads
    # .iloc[0] and expects a single value for the whole pull.
    df["fetched_at"] = fetched_at

    return df


def run_ingestion(start_date: datetime | None = None) -> pd.DataFrame:
    """Fetch weekly windows, write raw JSON, clean CSV and ingestion log."""
    if start_date is None:
        start_date = datetime.now()

    fetched_at = datetime.now().isoformat(timespec="seconds")

    all_events = []
    log_records = []
    seen_ids = set()

    for i in range(N_WEEKS):
        window_start = start_date + timedelta(days=7 * i)
        window_end = window_start + timedelta(days=7)

        start_iso = window_start.strftime("%Y-%m-%dT00:00:00Z")
        end_iso = window_end.strftime("%Y-%m-%dT23:59:59Z")

        print(f"Fetching week {i + 1}/{N_WEEKS}: {start_iso[:10]} to {end_iso[:10]}...")

        fetched_events, total_reported = fetch_window(start_iso, end_iso)

        for event in fetched_events:
            ev_id = event.get("id")
            if ev_id and ev_id not in seen_ids:
                seen_ids.add(ev_id)
                all_events.append(event)

        log_records.append({
            "week_start": window_start.strftime("%Y-%m-%d"),
            "retrieved": len(fetched_events),
            "reported": total_reported,
            "truncated": total_reported > len(fetched_events),
        })

    with open(RAW_FILE, "w", encoding="utf-8") as f:
        json.dump(all_events, f, indent=2)
    print(f"\nSaved {len(all_events)} unique raw records to {RAW_FILE}")

    clean_df = parse_and_clean(all_events, fetched_at)
    clean_df.to_csv(CLEAN_FILE, index=False)
    print(f"Saved cleaned data ({len(clean_df)} rows) to {CLEAN_FILE}")

    log_df = pd.DataFrame(log_records)
    log_df.to_csv(LOG_FILE, index=False)
    print(f"Saved ingestion log to {LOG_FILE}")

    return log_df


if __name__ == "__main__":
    run_ingestion()