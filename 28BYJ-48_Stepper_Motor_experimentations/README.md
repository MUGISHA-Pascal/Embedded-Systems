# 28BYJ-48 Stepper Motor Experimentations

This repository contains Arduino and Python code examples for experimenting with the 28BYJ-48 stepper motor and ULN2003 driver board. The experiments demonstrate basic motor control including continuous rotation and precise angle positioning.

## Hardware Requirements

- Arduino board (Uno, Nano, etc.)
- 28BYJ-48 stepper motor with ULN2003 driver board
- Jumper wires
- 5V power supply (can use Arduino's 5V output for testing)

## Wiring

Connect the ULN2003 driver to the Arduino as follows:

- IN1 → Digital Pin 8
- IN2 → Digital Pin 9
- IN3 → Digital Pin 10
- IN4 → Digital Pin 11
- + (5V) → 5V
- - (GND) → GND

## Experiments

### 1. Rotating Stepper Motor

**Location**: `/rotating_stepper_experimentation/`

This example demonstrates continuous rotation of the stepper motor in both clockwise and counter-clockwise directions.

**Features**:
- Continuous rotation with configurable speed
- Serial monitor feedback
- Simple loop for demonstration

**Usage**:
1. Upload `arduino_codes.ino` to your Arduino
2. Open Serial Monitor (9600 baud)
3. The motor will rotate clockwise, then counter-clockwise in a loop

### 2. Specific Angle Control

**Location**: `/specific_angle_experimentation/`

This example allows precise control of the stepper motor's position by specifying rotation angles.

**Features**:
- Angle-based positioning
- Serial communication for commands
- Two implementations:
  - Arduino-only control (`arduino_codes.ino`)
  - Python script for computer control (`python_codes.py`)

**Arduino-Only Usage**:
1. Upload `arduino_codes.ino` to your Arduino
2. Open Serial Monitor (9600 baud)
3. Enter the desired angle (positive for clockwise, negative for counter-clockwise)
4. Press Enter to execute the movement

**Python Control Usage**:
1. Upload `arduino_codes.ino` to your Arduino
2. Run `python_codes.py`
3. Enter the desired angle when prompted
4. Type 'q' to quit

## Notes

- The 28BYJ-48 motor has a gear reduction ratio of 1/64
- The motor requires 2048 steps for one full revolution (32 steps/rev × 64:1 gear ratio)
- The ULN2003 driver board has built-in LEDs that show the current coil activation pattern
- For smoother operation, ensure the motor is properly powered (external 5V power supply recommended for continuous use)

## Troubleshooting

- If the motor doesn't move, check all connections and ensure the correct pin order in the code
- If the motor vibrates but doesn't rotate, the speed might be too high - try reducing the speed value
- For the Python script, ensure you have the correct serial port configured

## Dependencies

- Arduino IDE with Stepper library (included by default)
- Python 3.x with pyserial package (for Python control)
  ```
  pip install pyserial
  ```

## License

This project is open source and available under the MIT License.
