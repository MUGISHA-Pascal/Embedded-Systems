import serial, time
arduino = serial.Serial(port="/dev/ttyACM0", baudrate=9600, timeout=1)
time.sleep(2)
STEPS_PER_REV = 350
def degrees_to_steps(deg):
    return int((deg / 360) * STEPS_PER_REV)
def send_degrees(degrees):
    steps = degrees_to_steps(degrees)
    arduino.write(f"{steps}\n".encode())
    print(f"Sent {degrees}° ({steps} steps) to Arduino")
while True:
    deg = input("Enter degrees (+/-), q to quit: ")
    if deg.lower() == "q":
        break
    try:
        send_degrees(float(deg))
    except ValueError:
        print("Invalid input")