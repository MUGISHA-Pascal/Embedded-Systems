# Automatic Gate Demo Kit

This repository contains Arduino code for an automatic gate system using an ultrasonic sensor.

## Functionality

The automatic gate system operates as follows:

- Uses an ultrasonic sensor to detect objects
- Opens the gate (servo rotates to 90°) when an object is detected within the threshold distance
- Closes the gate (servo returns to 0°) after 5 seconds of no detection
- Red LED indicates when gate is closed
- Blue LED indicates when gate is open
- Buzzer beeps continuously while gate is open

## Hardware Components

- Arduino Uno
- Ultrasonic sensor (HC-SR04)
- Servo motor
- Red and Blue LEDs
- Buzzer
- Connecting wires

## Pin Configuration

- Trigger Pin (Ultrasonic): 2
- Echo Pin (Ultrasonic): 3
- Red LED Anode: 4
- Red LED Cathode: 8
- Blue LED Cathode: 7
- Blue LED Pin: 5
- Servo Pin: 6
- Buzzer Pin: 12

## Dependencies

- Servo.h library (standard Arduino library)
