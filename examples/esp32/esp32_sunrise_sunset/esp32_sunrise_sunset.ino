// ESP32 + Arduino: today's sunrise and sunset from the Sunrise-Sunset.org API v2.
// Data by https://sunrise-sunset.org (attribution with a link is required
// wherever you display it).
//
// Needs the ArduinoJson library (version 7), from the Library Manager.
// Set your Wi-Fi name, password and coordinates below, upload, and open the
// Serial Monitor at 115200 baud.
//
// It uses plain HTTP, which the API supports for small devices that cannot
// do TLS. On an ESP32 you can also use https:// with WiFiClientSecure.

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* WIFI_SSID     = "your-wifi-name";
const char* WIFI_PASSWORD = "your-wifi-password";

// Your location in decimal degrees.
const char* LAT = "39.74";
const char* LNG = "-104.99";

void fetchSunTimes() {
  // No date: the API answers for "today" in the place's own local timezone.
  String url = String("http://api.sunrise-sunset.org/v2?lat=") + LAT + "&lng=" + LNG;

  HTTPClient http;
  http.begin(url);
  int status = http.GET();

  if (status == 429) {
    // Too many requests: wait the number of seconds in Retry-After.
    Serial.println("Rate limited, try again later.");
    http.end();
    return;
  }
  if (status != 200) {
    Serial.printf("HTTP error %d\n", status);
    http.end();
    return;
  }

  // The full answer has many fields; keep only the ones we use to save memory.
  JsonDocument filter;
  filter["date"] = true;
  filter["tzid"] = true;
  filter["sunrise"] = true;
  filter["sunset"] = true;
  filter["sun_status"] = true;

  JsonDocument doc;
  DeserializationError error = deserializeJson(doc, http.getString(), DeserializationOption::Filter(filter));
  http.end();
  if (error) {
    Serial.print("JSON error: ");
    Serial.println(error.c_str());
    return;
  }

  // Times look like "2026-10-14T08:24:05+02:00" (local time of the place).
  // They are null when the event does not happen (polar day or night).
  const char* sunrise = doc["sunrise"] | "none today";
  const char* sunset  = doc["sunset"]  | "none today";

  Serial.printf("Date:    %s (%s)\n", doc["date"].as<const char*>(), doc["tzid"].as<const char*>());
  Serial.printf("Sunrise: %s\n", sunrise);
  Serial.printf("Sunset:  %s\n", sunset);
  Serial.printf("Status:  %s\n", doc["sun_status"].as<const char*>());
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected.");

  fetchSunTimes();
}

void loop() {
  // The times only change once a day: asking every few hours is plenty.
  delay(6UL * 60 * 60 * 1000);
  fetchSunTimes();
}
