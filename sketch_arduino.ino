#include <WiFi.h>
#include <HTTPClient.h>

// Replace with your WiFi credentials
const char* ssid = "Etisalat 4G Router_d901";
const char* password = "pstfp83753";

// Local server endpoint
const char* serverName = "http://192.168.0.102:5000/update";

// Moisture sensor pins
const int moisturePin1 = 32; // Safe analog pin
const int moisturePin2 = 33; // Safe analog pin
const int moisturePin3 = 34; // Safe analog pin
const int moisturePin4 = 35; // Safe analog pin

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected!");
}

void loop() {
  int moistureValue[4] = {
    analogRead(moisturePin1),
    analogRead(moisturePin2),
    analogRead(moisturePin3),
    analogRead(moisturePin4)
  };

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    // JSON payload
    String jsonData = "{";
    jsonData += "\"pipes\": [";
    for (int i = 0; i < 4; i++) {
      jsonData += "{";
      jsonData += "\"pipe_id\":" + String(i + 1) + ",";
      jsonData += "\"moisture\":" + String(moistureValue[i]);
      jsonData += "},";
    }
    jsonData.remove(jsonData.length() - 1); // Remove trailing comma
    jsonData += "]}";

    Serial.println(jsonData);

    int httpResponseCode = http.POST(jsonData);
    if (httpResponseCode > 0) {
      Serial.println("POST successful");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("POST failed: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  }

  delay(5000); // Wait 5 seconds before next post
}
