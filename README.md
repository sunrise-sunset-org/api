# Sunrise-Sunset.org API

The free [Sunrise-Sunset.org API](https://sunrise-sunset.org/api) on GitHub:
sunrise, sunset, twilight, golden hour, solar position and moon data for any
place on Earth. Here you find ready-to-run examples, the OpenAPI spec, the
announcements of every change and a place to report problems.

**Stay up to date:** click *Watch* → *Custom* → *Releases* at the top of this
page and GitHub will tell you whenever the API changes.

- **Free.** No sign up, no API key.
- **Simple.** You send a latitude and longitude, you get JSON back.
- **Attribution required.** Show a visible link to [sunrise-sunset.org](https://sunrise-sunset.org) wherever you display the data.

## Contents

- [Quick start](#quick-start-30-seconds)
- [v1 or v2?](#v1-or-v2)
- [Common pitfalls](#common-pitfalls)
- [Examples](#examples)
- [For AI assistants (MCP)](#for-ai-assistants-mcp)
- [Usage limits and attribution](#usage-limits-and-attribution)
- [Reporting problems](#reporting-problems)
- [License](#license)

## Quick start (30 seconds)

Paste this into a terminal (or open the URL in your browser):

```sh
curl "https://api.sunrise-sunset.org/v2?lat=39.74&lng=-104.99&date=2026-08-15"
```

`lat` and `lng` are the latitude and longitude of the place, in decimal
degrees (these are Denver, Colorado). You get back something like this
(shortened):

```json
{
  "date": "2026-08-15",
  "tzid": "America/Denver",
  "utc_offset": "-06:00",
  "sunrise": "2026-08-15T06:12:13-06:00",
  "sunset": "2026-08-15T19:55:56-06:00",
  "solar_noon": "2026-08-15T13:04:24-06:00",
  "day_length": 49423,
  "sun_status": "normal",
  "dawn": "2026-08-15T05:43:20-06:00",
  "dusk": "2026-08-15T20:24:43-06:00",
  "golden_hour": {
    "morning": { "begin": "2026-08-15T05:54:37-06:00", "end": "2026-08-15T06:49:15-06:00" },
    "evening": { "begin": "2026-08-15T19:19:00-06:00", "end": "2026-08-15T20:13:28-06:00" }
  },
  "moon_phase": "Waxing Crescent",
  "moon_illumination": 11.25
}
```

How to read it:

- Times use the ISO 8601 format. `2026-08-15T06:12:13-06:00` means 15 August
  2026 at 06:12:13, local time, 6 hours behind UTC (the world reference
  time). Every programming language can read this format.
- The times are already in the **local time of the place**. You do not need
  to work out its timezone yourself: `tzid` tells you which one it is.
- `day_length` is in seconds (48841 seconds is 13 h 34 min).
- Leave out `date` to get today (today in that place, not where your server is).

Other parameters: `date=tomorrow`, `date_start` + `date_end` for a range of up
to 366 days, `tz` to get the times in a different timezone, and
`time_format=unix` for Unix timestamps. Every field is explained in the
[documentation](https://sunrise-sunset.org/api).

## v1 or v2?

There are two versions. **Use v2 for anything new.**

| | v2: `/v2` (recommended) | v1: `/json` (classic) |
|---|---|---|
| Times are in | the place's local time | UTC, unless you pass `tzid` |
| Time format | always ISO 8601 | `1:23:45 PM` by default, ISO 8601 with `formatted=0` |
| Events that do not happen (polar day or night) | `null` | `1970-01-01...` timestamps |
| Many days at once | yes, up to 366 per request | no, one request per day |
| Golden hour, blue hour, solar position, moon | yes | no |
| Errors | HTTP 400 with a readable message | `status` field, e.g. `INVALID_REQUEST` |

v1 is supported indefinitely and keeps working exactly as it does today, so
existing code will not break. It also keeps its original calculation, so its
sunrises are a little early and its sunsets a little late (by up to several
minutes, depending on place and date). v2 fixes that.

Migration table and v1 docs: [v2 docs, "Migrating from v1"](https://sunrise-sunset.org/api#migration)
and [v1 documentation](https://sunrise-sunset.org/api/v1).

## Common pitfalls

These are the problems we see most often in real integrations.

### 1. "The times are off by a few hours" (v1)

v1 answers in **UTC** unless you pass `tzid`. v2 answers in the place's
local time by default. The same day in Denver:

```
v1  /json?lat=39.74&lng=-104.99&date=2026-08-15&formatted=0  ->  "sunrise": "2026-08-15T12:11:02+00:00"
v2  /v2?lat=39.74&lng=-104.99&date=2026-08-15                ->  "sunrise": "2026-08-15T06:12:13-06:00"
```

(The two are also about a minute apart: that is the v1 calculation issue
mentioned above.)

In v2, `tz` must be a full timezone name like `America/Los_Angeles`.
Abbreviations like `PST` are rejected with HTTP 400, so mistakes do not go
unnoticed.

### 2. "Sunrise is on 1 January 1970" (v1)

Near the poles, on some days the sun never rises or never sets, and some
twilights never happen. v1 still answers `"status": "OK"` but fills those
fields with `1970-01-01T00:00:00+00:00` or `1970-01-01T00:00:01+00:00`.
Treat any 1970 date from v1 as "does not happen". Also, during the midnight
sun v1 reports `day_length` 0.

v2 returns `null` instead and tells you why in `sun_status`. Utqiagvik, Alaska,
on 21 December 2026:

```json
{ "date": "2026-12-21", "tzid": "America/Anchorage", "sun_status": "polar_night",
  "sunrise": null, "sunset": null, "day_length": 0 }
```

`sun_status` is `normal`, `midnight_sun` (`day_length` 86400) or
`polar_night` (`day_length` 0). Every event can be `null` on its own: near
the polar circles the sun can rise one day without setting. Check each field
before using it, and never work one out from another.

### 3. One request per day

If you show the same place every day, do not call the API every day. Ask for
the whole year **once** with `date_start` and `date_end`:

```sh
curl "https://api.sunrise-sunset.org/v2?lat=39.74&lng=-104.99&date_start=2027-01-01&date_end=2027-12-31"
```

You get `{"tzid", "lat", "lng", "days": [...]}` with one entry per day. A range
counts as a single request. Find days by their `date` field rather than by
position: in rare cases a calendar day never existed in a place (Samoa
skipped 30 December 2011) and it is left out.

### 4. Asking again for the same answer

The times for an explicit date never change, so save the response and reuse
it forever. Responses for `today` and `tomorrow` can be kept until local
midnight. The API sends the right `Cache-Control` headers, so browsers do
this on their own.

### 5. HTTP 429 "Too many requests"

The API allows about 5 requests per second. The limit is mostly there so
that a script stuck in a loop cannot slow the service down for everyone else:
normal use never gets near it. Above that you get HTTP 429 with a
`Retry-After: 1` header: wait 1 second and retry, and if you get 429 again,
double the wait each time (2, 4, 8 seconds...). The
[Python](examples/python/sun_times.py) and
[JavaScript](examples/javascript/sun-times.mjs) examples already do this. If
you see 429s often, check your code for a loop, then fetch date ranges
(pitfall 3) and cache the answers (pitfall 4).

### 6. Showing the time in the wrong timezone (JavaScript)

`new Date(data.sunrise)` reads the time correctly, but displaying that Date
shows it in the **viewer's** timezone. If you want the place's own clock
time, read it from the string: `data.sunrise.slice(11, 16)` gives `"07:34"`.

### 7. `!secret` inside the URL (Home Assistant)

In Home Assistant, `!secret` only works as a whole YAML value. Written inside
a URL, as in `resource: https://api.sunrise-sunset.org/json?lat=!secret home_lat&...`,
it is sent literally. v1 reads that text as latitude 0 and longitude 0 and
answers with the times of a point in the Atlantic, off the coast of Africa,
with no error. Build the URL with `resource_template` and your home zone
instead, as the [Home Assistant example](examples/home-assistant/sunrise_sunset.yaml) does:

```yaml
resource_template: >-
  https://api.sunrise-sunset.org/v2?lat={{ state_attr('zone.home', 'latitude') }}&lng={{ state_attr('zone.home', 'longitude') }}
```

v2 rejects a latitude that is not a number with HTTP 400, so this kind of
mistake shows up at once.

## Examples

All examples use v2 and were tested against the live API.

| Folder | What it shows |
|---|---|
| [examples/curl.sh](examples/curl.sh) | Today, a date, a whole year, Unix timestamps, polar night, an error |
| [examples/python/](examples/python/sun_times.py) | Standard library only. Retries on 429, caches a full year in a file |
| [examples/javascript/](examples/javascript/) | `sun-times.mjs` for Node.js 18+, `browser.html` for a web page (no server needed) |
| [examples/home-assistant/](examples/home-assistant/sunrise_sunset.yaml) | REST sensors: sunrise, sunset, dawn, dusk, golden hour, moon phase |
| [examples/esp32/](examples/esp32/esp32_sunrise_sunset/esp32_sunrise_sunset.ino) | ESP32 + ArduinoJson over plain HTTP |
| [examples/mcp/](examples/mcp/README.md) | Connecting AI assistants (Claude, ChatGPT, Cursor, Codex) |
| [openapi.json](openapi.json) | OpenAPI spec, for code generators and API tools |

Run them:

```sh
./examples/curl.sh                              # optional: ./examples/curl.sh 40.71 -74.01
python3 examples/python/sun_times.py 40.71 -74.01
node examples/javascript/sun-times.mjs 40.71 -74.01
```

Real output of the Python example for New York (run on 14 October 2026):

```
Today (2026-10-14, America/New_York):
  sunrise 07:06, sunset 18:17
  evening golden hour 17:40 to 18:34
  moon: Waxing Crescent (15.57% lit)

2027: 365 days fetched in one request.
  shortest day: 2027-12-21 (9.3 hours of daylight)
  2027-06-21: sunrise 05:25, sunset 20:30

Utqiagvik on 2026-12-21: sun_status=polar_night, sunrise=None, day_length=0
```

**Plain HTTP** (`http://api.sunrise-sunset.org`) works too, for IoT and
embedded devices that cannot make TLS connections. Use HTTPS everywhere else.

**From a web page**, you can call the API directly with `fetch()`: requests
from any website are allowed (CORS).

## For AI assistants (MCP)

The same data is available as an MCP server, so AI assistants and agents can
use it as a tool. No API key needed. Server URL:

```
https://api.sunrise-sunset.org/mcp
```

Claude Code:

```sh
claude mcp add --transport http sunrise-sunset https://api.sunrise-sunset.org/mcp
```

Setup for Claude, ChatGPT, Codex and Cursor: [examples/mcp](examples/mcp/README.md)
and the [MCP guide](https://sunrise-sunset.org/mcp).

## Usage limits and attribution

- The API is free for reasonable request volumes. Use date ranges and caching
  to stay well under the limits.
- **Attribution is required**: show a visible link to
  [sunrise-sunset.org](https://sunrise-sunset.org) in the app or page where
  you show the data. For example:

  ```html
  Sun data by <a href="https://sunrise-sunset.org">Sunrise-Sunset.org</a>
  ```

- Is the API down? Check the [API status page](https://apistatus.sunrise-sunset.org/).

## Reporting problems

Found a wrong time, a confusing response or a broken example?
[Open an issue](../../issues/new/choose) in this repository. Include the full
request URL, what you expected, what you got, and the date and timezone you
had in mind.

For other questions, use the [contact page](https://sunrise-sunset.org/contact).

## License

The **example code** in this repository is under the [MIT License](LICENSE):
copy it into your own projects freely.

The license covers the code only. The **data** returned by the API has its own
terms: it is free to use with the attribution described above. See the
[API documentation](https://sunrise-sunset.org/api#rate-limits).
