Exemple d'envoi de mesures depuis un ESP32 vers l'endpoint Django

But: envoyer un POST JSON sur

  http://<server>/esp32/ingest/

Header requis:
  X-ESP32-KEY: <clé configurée dans settings.ESP32_API_KEY>

Payload JSON attendu:
  {
    "filtre": <id_filtre>,
    "nom": "nom_du_capteur",
    "type": "temp",
    "valeur": "23.5"
  }

Exemple Arduino (ESP32) utilisant la librairie ArduinoHttpClient + WiFi.h:

```cpp
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASS";
const char* serverUrl = "http://192.168.1.10:8000/esp32/ingest/"; // changez l'IP
const char* espKey = "change_me"; // doit correspondre à ESP32_API_KEY dans settings

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-ESP32-KEY", espKey);

    String payload = "{\"filtre\": 1, \"nom\": \"esp32_temp\", \"type\": \"temp\", \"valeur\": \"24.7\"}";

    int httpCode = http.POST(payload);
    if (httpCode > 0) {
      String resp = http.getString();
      Serial.println(httpCode);
      Serial.println(resp);
    } else {
      Serial.println("Error on HTTP request");
    }
    http.end();
  }
  delay(15000); // envoyer toutes les 15s
}
```

Notes:
- Assurez-vous que l'ESP32 et le serveur Django sont sur le même réseau ou que le serveur est accessible depuis l'ESP32.
- Pour la production, utilisez HTTPS et une clé plus forte. Cette méthode est un point de départ simple.
