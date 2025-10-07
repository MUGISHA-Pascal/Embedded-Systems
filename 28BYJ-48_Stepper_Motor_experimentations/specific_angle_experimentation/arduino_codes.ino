#include <Stepper.h>
const int stepsPerRevolution = 2048;  // 28BYJ-48 full revolution
Stepper myStepper(stepsPerRevolution, 8, 10, 9, 11); // check order for direction
void setup() {
  myStepper.setSpeed(10);   // RPM
  Serial.begin(9600);
  Serial.println("Stepper ready. Send degrees (+/-):");
}
void loop() {
  if (Serial.available() > 0) {
    long degrees = Serial.parseInt();   // Read degrees from serial
    if (degrees != 0) {
      long steps = (degrees * stepsPerRevolution) / 360; // convert degrees to steps
      Serial.print("Moving ");
      Serial.print(degrees);
      Serial.print(" degrees (");
      Serial.print(steps);
      Serial.println(" steps)");
      myStepper.step(steps);
      Serial.println("Done!");
    }
  }
}