#include <DHT.h>

#define DHTPIN 3        // Data pin connected to digital pin 3
#define DHTTYPE DHT11
#define POWER_PIN 2     // Power pin for DHT sensor
#define GND_PIN 4       // "Fake" ground pin set to LOW
#define LED_PIN 13      // On-board LED

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // Powering DHT11
  pinMode(POWER_PIN, OUTPUT);
  digitalWrite(POWER_PIN, HIGH); // Simulate 5V

  // Simulate GND
  pinMode(GND_PIN, OUTPUT);
  digitalWrite(GND_PIN, LOW); // Simulate ground

  dht.begin();
}

void loop() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (!isnan(humidity) && !isnan(temperature)) {
    Serial.print("TEMP:");
    Serial.print(temperature);
    Serial.print(",HUM:");
    Serial.println(humidity);
  } else {
    Serial.println("Failed to read from DHT sensor!");
  }

  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command == "LED_ON") {
      digitalWrite(LED_PIN, HIGH);
    } else if (command == "LED_OFF") {
      digitalWrite(LED_PIN, LOW);
    }
  }

  delay(2000);  // Read every 2 seconds
}
