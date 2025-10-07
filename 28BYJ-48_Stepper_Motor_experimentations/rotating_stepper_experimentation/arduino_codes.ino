#include <Stepper.h>
// Number of steps per revolution for 28BYJ-48 stepper motor
const int stepsPerRevolution = 2048;
// Define ULN2003 input pins connected to Arduino
const int IN1 = 8;
const int IN2 = 9;
const int IN3 = 10;
const int IN4 = 11;
// Initialize the stepper with the above pins
Stepper myStepper(stepsPerRevolution, IN1, IN3, IN2, IN4);
// NOTE: Order of pins matters! (IN1, IN3, IN2, IN4 works for ULN2003 + 28BYJ-48)
void setup() {
  myStepper.setSpeed(10); // speed in RPM (try 10–15 first)
  Serial.begin(9600);
}
void loop() {
  Serial.println("Rotating clockwise...");
  myStepper.step(stepsPerRevolution);  // one full revolution CW
  delay(1000);
  Serial.println("Rotating counterclockwise...");
  myStepper.step(-stepsPerRevolution); // one full revolution CCW
  delay(1000);
}