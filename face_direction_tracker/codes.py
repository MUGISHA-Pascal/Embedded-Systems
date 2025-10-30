import cv2
import os
import time

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path to the Haar Cascade XML file
cascade_path = os.path.join(script_dir, 'haarcascade_frontalface_default.xml')

# Load the Haar Cascade face detector
if not os.path.exists(cascade_path):
    # If the cascade file doesn't exist, try to download it
    import urllib.request
    url = 'https://raw.githubusercontent.com/opencv/opencv/4.x/data/haarcascades/haarcascade_frontalface_default.xml'
    urllib.request.urlretrieve(url, cascade_path)

face_cascade = cv2.CascadeClassifier(cascade_path)

# Open webcam
cap = cv2.VideoCapture(0)

prev_cx, prev_cy = None, None  # store previous face center
prev_time = time.time()        # for speed calculation

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    direction = "Center"
    speed = 0

    for (x, y, w, h) in faces:
        # Draw green box around the face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Find face center
        cx = x + w // 2
        cy = y + h // 2

        # Draw center point
        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

        # If we have previous center, calculate movement
        if prev_cx is not None and prev_cy is not None:
            dx = cx - prev_cx
            dy = cy - prev_cy

            # Determine direction
            if abs(dx) > abs(dy):
                direction = "Right" if dx > 10 else "Left" if dx < -10 else "Center"
            else:
                direction = "Down" if dy > 10 else "Up" if dy < -10 else "Center"

            # Compute speed (pixels per second)
            current_time = time.time()
            dt = current_time - prev_time
            if dt > 0:
                speed = int(((dx ** 2 + dy ** 2) ** 0.5) / dt)

            prev_time = current_time

        prev_cx, prev_cy = cx, cy

    # Display direction and speed
    cv2.putText(frame, f"Direction: {direction}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Speed: {speed} px/s", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Face Direction Tracker", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
