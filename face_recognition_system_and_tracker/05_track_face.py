#!/usr/bin/env python3
import cv2
import time
import numpy as np
import sys
import serial

# -------------------------- CONFIG --------------------------
CASCADE_PATH = 'models/haarcascade_frontalface_default.xml'
CAM_IDX = 0                   # webcam index
FRAME_SIZE = (800, 600)
FONT = cv2.FONT_HERSHEY_SIMPLEX
SERIAL_PORT = '/dev/ttyACM0'          # <-- change this to your Arduino port (e.g., /dev/ttyUSB0 on Linux)
BAUD_RATE = 9600
ROTATE_STEP = 5               # degrees per adjustment
THRESHOLD = 100               # pixels from center before adjusting
# -------------------------------------------------------------

def main():
    # ---- Connect to Arduino ----
    try:
        arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # wait for Arduino to reset
        print(f"[OK] Connected to Arduino on {SERIAL_PORT}")
    except Exception as e:
        print("[ERROR] Could not connect to Arduino:", e)
        arduino = None

    # ---- Load cascade ----
    cascade = cv2.CascadeClassifier(CASCADE_PATH)
    if cascade.empty():
        sys.exit(f"[ERROR] Could not load cascade: {CASCADE_PATH}")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_SIZE[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_SIZE[1])
    if not cap.isOpened():
        sys.exit("[ERROR] Cannot open camera")

    frame_center_x = FRAME_SIZE[0] // 2
    last_cmd_time = 0

    print("Press 'q' to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Frame capture failed.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

        if len(faces) > 0:
            x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
            cx = x + w // 2

            # Draw face box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (cx, y + h // 2), 5, (0, 0, 255), -1)

            offset = cx - frame_center_x

            # Only send a command if face is far from center
            if abs(offset) > THRESHOLD and (time.time() - last_cmd_time > 1):
                if offset < 0:
                    command = f"CCW {ROTATE_STEP}\n"
                    print("Face left → Rotate CCW")
                else:
                    command = f"CW {ROTATE_STEP}\n"
                    print("Face right → Rotate CW")

                if arduino:
                    arduino.write(command.encode('utf-8'))
                last_cmd_time = time.time()

        # Draw center line
        cv2.line(frame, (frame_center_x, 0), (frame_center_x, FRAME_SIZE[1]), (255, 0, 0), 2)

        cv2.imshow("Face Tracker", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    if arduino:
        arduino.close()

if __name__ == "__main__":
    main()
