import cv2
import time

# Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize video capture
cap = cv2.VideoCapture(0)

# Variables to store previous face center and timestamp
prev_cx, prev_cy = None, None
prev_time = time.time()

while True:
    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Current timestamp
    current_time = time.time()
    time_diff = current_time - prev_time if prev_time is not None else 1.0

    # Process detected faces
    direction = ""
    speed = 0.0
    for (x, y, w, h) in faces:
        # Draw green bounding box
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Calculate center of the face
        cx = x + w // 2
        cy = y + h // 2

        # Draw center point
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        # If previous center exists, calculate direction and speed
        if prev_cx is not None and prev_cy is not None:
            dx = cx - prev_cx
            dy = cy - prev_cy

            # Determine direction (inverted)
            if abs(dx) > 10 or abs(dy) > 10:  # Threshold to avoid noise
                if abs(dx) > abs(dy):
                    direction = "Left" if dx > 0 else "Right"
                else:
                    direction = "Up" if dy > 0 else "Down"

            # Calculate speed (pixels per second)
            distance = ((dx ** 2) + (dy ** 2)) ** 0.5
            speed = distance / time_diff if time_diff > 0 else 0
            
            # Print direction and speed to console
            if direction:
                print(f"Direction: {direction}, Speed: {speed:.2f} px/s")

        # Update previous center and time
        prev_cx, prev_cy = cx, cy
        prev_time = current_time
        break  # Process only the first detected face

    # Display direction and speed
    text = f"Direction: {direction}, Speed: {speed:.2f} px/s"
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Show the frame
    cv2.imshow('Face Direction Tracker', frame)

    # Break loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()