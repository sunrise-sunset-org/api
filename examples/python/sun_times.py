#!/usr/bin/env python3
"""Sunrise-Sunset.org API v2 example, standard library only (Python 3.8+).

Data by https://sunrise-sunset.org (attribution with a link is required
wherever you display it).

Usage:
    python3 sun_times.py                 # Denver, Colorado
    python3 sun_times.py 40.71 -74.01    # any latitude and longitude

What it shows:
  * one day, with times already in the place's local timezone
  * a whole year in ONE request, saved to a file and reused next time
  * polite handling of HTTP 429 (rate limited) using Retry-After
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

API = "https://api.sunrise-sunset.org/v2"
# A descriptive User-Agent is good manners: it tells us which app is calling.
USER_AGENT = "my-sun-app/1.0"


def get_json(params, max_attempts=4):
    """GET the v2 endpoint and return the parsed JSON.

    Retries on 429 (too many requests), waiting for the number of seconds in
    the Retry-After header, or with exponential backoff if it is missing.
    Raises ValueError with the API's own message for 400 errors.
    """
    url = API + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(max_attempts):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as err:
            if err.code == 429 and attempt < max_attempts - 1:
                retry_after = err.headers.get("Retry-After")
                wait = int(retry_after) if retry_after and retry_after.isdigit() else 2 ** attempt
                print(f"Rate limited, waiting {wait}s before retrying...", file=sys.stderr)
                time.sleep(wait)
                continue
            if err.code == 400:
                body = json.load(err)
                raise ValueError(f"{body['error']}: {body['message']}") from None
            raise
    raise RuntimeError("unreachable")


def get_year(lat, lng, year):
    """Return the whole year for one place, using a local file as cache.

    Times for an explicit date never change, so the file can be kept forever.
    """
    cache_file = f"sun_{lat}_{lng}_{year}.json"
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            return json.load(f)
    data = get_json({
        "lat": lat,
        "lng": lng,
        "date_start": f"{year}-01-01",
        "date_end": f"{year}-12-31",
    })
    with open(cache_file, "w") as f:
        json.dump(data, f)
    return data


def hhmm(iso_time):
    """'2026-08-15T07:34:53+02:00' -> '07:34'. None (event does not happen) -> '--:--'."""
    if iso_time is None:
        return "--:--"
    return datetime.fromisoformat(iso_time).strftime("%H:%M")


def main():
    lat = float(sys.argv[1]) if len(sys.argv) > 1 else 39.74
    lng = float(sys.argv[2]) if len(sys.argv) > 2 else -104.99

    # 1. Today. No tz needed: v2 answers in the place's local timezone.
    today = get_json({"lat": lat, "lng": lng})
    print(f"Today ({today['date']}, {today['tzid']}):")
    print(f"  sunrise {hhmm(today['sunrise'])}, sunset {hhmm(today['sunset'])}")
    evening = today["golden_hour"]["evening"]
    print(f"  evening golden hour {hhmm(evening['begin'])} to {hhmm(evening['end'])}")
    print(f"  moon: {today['moon_phase']} ({today['moon_illumination']}% lit)")

    # 2. A whole year in one request, instead of one request per day.
    year = datetime.now().year + 1
    data = get_year(lat, lng, year)
    days = {day["date"]: day for day in data["days"]}  # match days by date
    shortest = min(data["days"], key=lambda d: d["day_length"] if d["day_length"] is not None else 10**9)
    print(f"\n{year}: {len(days)} days fetched in one request.")
    print(f"  shortest day: {shortest['date']} ({shortest['day_length'] / 3600:.1f} hours of daylight)")
    june21 = days.get(f"{year}-06-21")
    if june21:
        print(f"  {june21['date']}: sunrise {hhmm(june21['sunrise'])}, sunset {hhmm(june21['sunset'])}")

    # 3. Near the poles some events do not happen: v2 returns null (None).
    polar = get_json({"lat": 71.29, "lng": -156.79, "date": "2026-12-21"})
    print(f"\nUtqiagvik on {polar['date']}: sun_status={polar['sun_status']}, "
          f"sunrise={polar['sunrise']}, day_length={polar['day_length']}")

    print("\nSun data by https://sunrise-sunset.org")


if __name__ == "__main__":
    main()
