#include <Arduino.h>
// === CONFIGURATION ===
int IN1 = 8;
int IN2 = 9;
int IN3 = 10;
int IN4 = 11;
int delayTime = 5; // delay between steps (ms) - increase if motor skips
// 8-step half-step sequence for 28BYJ-48
int steps[8][4] = {
  {1, 0, 0, 1},
  {1, 0, 0, 0},
  {1, 1, 0, 0},
  {0, 1, 0, 0},
  {0, 1, 1, 0},
  {0, 0, 1, 0},
  {0, 0, 1, 1},
  {0, 0, 0, 1}
};
void setup() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  Serial.begin(9600);
  Serial.println("Stepper control ready. Send L/R/S commands.");
}
void stepMotor(int step) {
  digitalWrite(IN1, steps[step][0]);
  digitalWrite(IN2, steps[step][1]);
  digitalWrite(IN3, steps[step][2]);
  digitalWrite(IN4, steps[step][3]);
}
void rotateCW(int stepsCount) {
  for (int i = 0; i < stepsCount; i++) {
    for (int s = 0; s < 8; s++) {
      stepMotor(s);
      delay(delayTime);
    }
  }
}
void rotateCCW(int stepsCount) {
  for (int i = 0; i < stepsCount; i++) {
    for (int s = 7; s >= 0; s--) {
      stepMotor(s);
      delay(delayTime);
    }
  }
}
void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    // Flush any extra characters
    while (Serial.available() > 0) Serial.read();
    Serial.print("Received command: ");
    Serial.println(command);
    if (command == 'L' || command == 'l') {
      rotateCCW(5); // move small step left
    } else if (command == 'R' || command == 'r') {
      rotateCW(5);  // move small step right
    } else if (command == 'S' || command == 's') {
      Serial.println("Stop command - motor idle");
    } else {
      Serial.println("Unknown command");
    }
  }
}