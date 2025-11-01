import cv2
import serial
import time
# === CONFIGURATION ===
SERIAL_PORT = "COM9"      # <-- change to your Arduino port
BAUD_RATE = 9600
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
CENTER_TOLERANCE = 100    # pixels before movement
# === SETUP ===
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Wait for Arduino to initialize
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
cap = cv2.VideoCapture(0)
cap.set(3, FRAME_WIDTH)
cap.set(4, FRAME_HEIGHT)
print("Face tracking starting... Press 'q' to quit.")
while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 7, minSize=(120, 120))
    frame_center = FRAME_WIDTH // 2
    message = "No face detected so far"
    command = "S"  # stop (still)
    if len(faces) > 0:
        (x, y, w, h) = max(faces, key=lambda r: r[2]*r[3])
        cx = x + w // 2
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # cv2.circle(frame, (cx, cy), 8, (0, 0, 255), -1)
        # cv2.line(frame, (frame_center, 0), (frame_center, FRAME_HEIGHT), (255, 0, 0), 2)
        if cx < frame_center - CENTER_TOLERANCE:
            message = "Move left "
            command = "L"
        elif cx > frame_center + CENTER_TOLERANCE:
            message = "Moving right "
            command = "R"
        else:
            message = "Face is still in center"
            command = "S"
        cv2.putText(frame, f"Command: {message}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0, 0), 2)
        # Send command to Arduino
        ser.write(command.encode())
    cv2.imshow("Face trackng (Arduino Control)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
ser.close()















