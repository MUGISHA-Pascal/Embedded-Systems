#!/usr/bin/env python3
import cv2
import time
import os

# ---- Config ----
MAX_IMAGES = 300
INTERVAL_MS = 400
FRAME_SIZE = (800, 800)  # (w, h)
CASCADE_PATH = 'models/haarcascade_frontalface_default.xml'
DATASET_DIR = 'dataset'

# ---- Setup ----
os.makedirs(DATASET_DIR, exist_ok=True)

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
if face_cascade.empty():
    raise SystemExit(f"[Error] Could not load cascade at: {CASCADE_PATH}")
time.sleep(0.5)

ID = input('Enter your ID: ').strip()
print("Please get your face ready!")
time.sleep(2)

cam = cv2.VideoCapture(1)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_SIZE[0])
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_SIZE[1])
if not cam.isOpened():
    raise SystemExit("[Error] Could not open camera.")

win = "Dataset Generating..."
cv2.namedWindow(win)

start_time = time.time()
last_capture_ts = start_time
image_count = 0

# visual feedback flag
last_saved_flash_ts = 0.0
FLASH_MS = 200  # how long to show the 'Saved!' flash

while True:
    ok, frame = cam.read()
    if not ok:
        print("[Warn] Failed to read frame.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    # draw faces + capture
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 180, 0), 2)

        elapsed_ms = (time.time() - last_capture_ts) * 1000.0
        if elapsed_ms >= INTERVAL_MS and image_count < MAX_IMAGES:
            face_crop = gray[y:y + h, x:x + w]
            filename = os.path.join(
                DATASET_DIR, f"data.{ID}.{int(time.time() * 1000)}.jpg"
            )
            cv2.imwrite(filename, face_crop)
            image_count += 1
            last_capture_ts = time.time()
            last_saved_flash_ts = last_capture_ts  # trigger flash

            # Console feedback
            print(f"Saved [{image_count}/{MAX_IMAGES}]: {os.path.basename(filename)}")

            # Only take one capture per interval, even if multiple faces are found
            break

    # ---- HUD overlay ----
    # Top bar
    cv2.rectangle(frame, (0, 0), (frame.shape[1], 40), (0, 0, 0), -1)
    hud = f"ID: {ID}  |  Saved: {image_count}/{MAX_IMAGES}  |  Interval: {INTERVAL_MS} ms  |  Press 'q' to quit"
    cv2.putText(frame, hud, (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

    # Flash “Saved!” briefly after each write
    if (time.time() - last_saved_flash_ts) * 1000.0 <= FLASH_MS:
        text = "[OK]"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.8
        thickness = 2

        # Measure how wide/high the text will be
        (text_w, text_h), baseline = cv2.getTextSize(text, font, scale, thickness)

        # Add some padding around it
        pad_x, pad_y = 10, 10
        x, y = 20, 80  # top-left of the text box

        # Draw filled rectangle that matches text width
        cv2.rectangle(frame,
                    (x - pad_x, y - text_h - pad_y),
                    (x + text_w + pad_x, y + baseline + pad_y),
                    (0, 180, 0), -1)

        # Draw text on top
        cv2.putText(frame, text, (x, y), font, scale, (255, 255, 255), thickness, cv2.LINE_AA)

    # Simple progress bar at bottom
    bar_w = frame.shape[1] - 20
    pct = 0 if MAX_IMAGES == 0 else min(1.0, image_count / float(MAX_IMAGES))
    filled = int(bar_w * pct)
    y1 = frame.shape[0] - 20
    cv2.rectangle(frame, (10, y1), (10 + bar_w, y1 + 10), (255, 255, 255), 1)
    cv2.rectangle(frame, (10, y1), (10 + filled, y1 + 10), (0, 180, 0), -1)

    # Show
    cv2.imshow(win, frame)

    # Exit conditions
    if (cv2.waitKey(1) & 0xFF) == ord('q') or image_count >= MAX_IMAGES:
        break

cam.release()
cv2.destroyAllWindows()

print(f"\n√ Dataset generation complete.")
print(f"   ID: {ID}")
print(f"   Saved: {image_count} image(s) to '{DATASET_DIR}/'")