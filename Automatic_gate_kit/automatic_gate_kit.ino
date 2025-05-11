#include <Servo.h>

// Pin definitions
const int triggerPin = 2;
const int echoPin = 3;
const int redLedAnodePin = 4;
const int redLedCathodePin = 8;
const int blueLedCathodePin = 7;
const int blueLedPin = 5;
const int servoPin = 6;
const int buzzerPin = 12;

// Constants
const float thresholdDistance = 50.0;
const int closedAngle = 0;
const int openAngle = 90;
const unsigned long closeDelay = 5000; // 5 seconds before closing

Servo myServo;
bool isOpen = false;
unsigned long lastDetectionTime = 0;

// Buzzer timing
unsigned long lastBeepTime = 0;
bool buzzerOn = false;
const unsigned long beepOnTime = 50;   // 50ms ON
const unsigned long beepCycle = 500;   // Total cycle: 500ms

void setup() {
  pinMode(triggerPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(redLedAnodePin, OUTPUT);
  pinMode(redLedCathodePin, OUTPUT);
  pinMode(blueLedCathodePin, OUTPUT);
  digitalWrite(redLedCathodePin, LOW);
  digitalWrite(blueLedCathodePin, LOW);
  pinMode(blueLedPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  myServo.attach(servoPin);
  myServo.write(closedAngle);  // Start closed

  digitalWrite(redLedAnodePin, HIGH);  // Red ON
  digitalWrite(blueLedPin, LOW);       // Blue OFF
  digitalWrite(buzzerPin, LOW);        // Buzzer OFF
}

// Measure distance
float getDistance() {
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);
  long duration = pulseIn(echoPin, HIGH);
  return duration / 20.0;
}

void loop() {
  float distance = getDistance();
  bool objectDetected = (distance < thresholdDistance);
  unsigned long currentTime = millis();

  if (objectDetected) {
    if (!isOpen) {
      // Open the gate
      myServo.write(openAngle);
      isOpen = true;
      digitalWrite(redLedAnodePin, LOW);   // Red OFF
      digitalWrite(blueLedPin, HIGH);      // Blue ON
    }
    lastDetectionTime = currentTime;
  } else {
    // Object gone, check for 5 second timeout
    if (isOpen && (currentTime - lastDetectionTime > closeDelay)) {
      // Close the gate
      myServo.write(closedAngle);
      isOpen = false;
      digitalWrite(redLedAnodePin, HIGH);   // Red ON
      digitalWrite(blueLedPin, LOW);        // Blue OFF
      digitalWrite(buzzerPin, LOW);         // Stop buzzer
    }
  }

  // Gentle buzzer while gate is open (blue light ON)
  if (isOpen) {
    if (!buzzerOn && currentTime - lastBeepTime >= beepCycle) {
      digitalWrite(buzzerPin, HIGH);      // Short beep ON
      buzzerOn = true;
      lastBeepTime = currentTime;
    } else if (buzzerOn && currentTime - lastBeepTime >= beepOnTime) {
      digitalWrite(buzzerPin, LOW);       // Beep OFF
      buzzerOn = false;
    }
  }

  delay(50);  // Light operation delay
}