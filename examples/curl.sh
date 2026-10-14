#!/usr/bin/env bash
# Sunrise-Sunset.org API examples with curl.
# Data by https://sunrise-sunset.org (attribution with a link is required).
#
# Usage: ./curl.sh            (uses Malaga, Spain)
#        ./curl.sh 40.71 -74.01  (any latitude and longitude)
#
# jq is optional: if it is installed, the output is trimmed to a few fields.

set -euo pipefail

LAT="${1:-36.72}"
LNG="${2:--4.42}"
API="https://api.sunrise-sunset.org"

# Pretty-print with jq when available, otherwise print the start of the raw JSON.
show() {
  if command -v jq >/dev/null 2>&1; then jq "$1"; else cut -c1-300; fi
}

echo "== 1. Today, in the place's own local time =="
curl -s "$API/v2?lat=$LAT&lng=$LNG" \
  | show '{date, tzid, sunrise, sunset, day_length, sun_status}'

echo
echo "== 2. A specific date =="
curl -s "$API/v2?lat=$LAT&lng=$LNG&date=2026-12-21" \
  | show '{date, sunrise, sunset, golden_hour: .golden_hour.evening, moon_phase}'

echo
echo "== 3. A whole year in ONE request (instead of 365 requests) =="
curl -s "$API/v2?lat=$LAT&lng=$LNG&date_start=2027-01-01&date_end=2027-12-31" \
  | show '{tzid, days: (.days | length), first: .days[0].date, last: .days[-1].date}'

echo
echo "== 4. Times as Unix epoch seconds (handy for small devices) =="
curl -s "$API/v2?lat=$LAT&lng=$LNG&date=2026-12-21&time_format=unix" \
  | show '{date, tzid, sunrise, sunset}'

echo
echo "== 5. Polar night: events that do not happen are null in v2 =="
curl -s "$API/v2?lat=69.65&lng=18.96&date=2026-12-21" \
  | show '{date, tzid, sun_status, sunrise, sunset, day_length}'

echo
echo "== 6. Errors are plain HTTP status codes with a readable message =="
curl -s -w '\nHTTP status: %{http_code}\n' "$API/v2?lat=$LAT&lng=$LNG&tz=PST"
