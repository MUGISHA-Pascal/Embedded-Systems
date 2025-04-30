int relayPin = 2;

void setup() {
  Serial.begin(9600);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH); // Relay OFF initially
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "ON") {
      digitalWrite(relayPin, LOW); // Relay ON
    } else if (cmd == "OFF") {
      digitalWrite(relayPin, HIGH); // Relay OFF
    }
  }
}