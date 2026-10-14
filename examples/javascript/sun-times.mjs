// Sunrise-Sunset.org API v2 example with fetch(), for Node.js 18 or newer.
// Usage: node sun-times.mjs [lat] [lng]
// The two functions below work unchanged in a browser (see browser.html for
// a minimal web page).
//
// Data by https://sunrise-sunset.org (attribution with a link is required
// wherever you display it).

const API = 'https://api.sunrise-sunset.org/v2';

/**
 * GET the v2 endpoint and return the parsed JSON.
 * Retries on 429 (too many requests), waiting for Retry-After seconds,
 * or with exponential backoff if the header is missing.
 */
async function getSunTimes(params, maxAttempts = 4) {
  const url = `${API}?${new URLSearchParams(params)}`;
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const response = await fetch(url);
    if (response.ok) return response.json();

    if (response.status === 429 && attempt < maxAttempts - 1) {
      const retryAfter = Number(response.headers.get('Retry-After'));
      const waitSeconds = retryAfter > 0 ? retryAfter : 2 ** attempt;
      await new Promise((resolve) => setTimeout(resolve, waitSeconds * 1000));
      continue;
    }
    if (response.status === 400) {
      const body = await response.json(); // {error, message, docs}
      throw new Error(`${body.error}: ${body.message}`);
    }
    throw new Error(`HTTP ${response.status}`);
  }
}

/** '2026-08-15T07:34:53+02:00' -> '07:34' (the place's local time). null -> '--:--'. */
function hhmm(isoTime) {
  // The API already gives local time with its offset, so we read the clock
  // digits straight from the string. new Date(isoTime) also works, but then
  // formatting it shows the time in the VIEWER's timezone, not the place's.
  return isoTime === null ? '--:--' : isoTime.slice(11, 16);
}

// Demo
{
  const lat = process.argv[2] ?? '39.74';
  const lng = process.argv[3] ?? '-104.99';

  // 1. Today, already in the place's local timezone (no tz parameter needed).
  const today = await getSunTimes({ lat, lng });
  console.log(`Today (${today.date}, ${today.tzid}):`);
  console.log(`  sunrise ${hhmm(today.sunrise)}, sunset ${hhmm(today.sunset)}`);
  console.log(`  dawn ${hhmm(today.dawn)}, dusk ${hhmm(today.dusk)}`);

  // 2. A whole month in one request. Match entries by their date field.
  const month = await getSunTimes({ lat, lng, date_start: '2026-12-01', date_end: '2026-12-31' });
  const byDate = Object.fromEntries(month.days.map((day) => [day.date, day]));
  console.log(`\nDecember 2026: ${month.days.length} days in one request`);
  console.log(`  Dec 21: sunrise ${hhmm(byDate['2026-12-21'].sunrise)}, sunset ${hhmm(byDate['2026-12-21'].sunset)}`);

  // 3. Errors come back as HTTP 400 with a readable message.
  try {
    await getSunTimes({ lat, lng, tz: 'PST' });
  } catch (err) {
    console.log(`\nError example: ${err.message}`);
  }

  console.log('\nSun data by https://sunrise-sunset.org');
}
