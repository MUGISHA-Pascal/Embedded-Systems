#!/usr/bin/env python3
import cv2, sys, json, time, argparse
from pathlib import Path

# -------- Paths --------
ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"
MODEL_PATH = MODELS_DIR / "trained_lbph_face_recognizer_model.yml"
CASCADE_PATH = MODELS_DIR / "haarcascade_frontalface_default.xml"
LABELMAP_PATH = MODELS_DIR / "label_map.json"

# -------- CLI --------
ap = argparse.ArgumentParser(description="LBPH Face Recognition (predict).")
ap.add_argument("--threshold", type=float, default=80.0,
                help="Distance cutoff: <= threshold → candidate match; > threshold → Unknown")
ap.add_argument("--min-conf", type=float, default=10.0,
                help="Minimum confidence percentage (0-100) to accept a match (default: 25)")
ap.add_argument("--camera", type=int, default=1,
                help="Camera index (default 1). Ignored if --image is set.")
ap.add_argument("--image", type=str,
                help="Run on a single image instead of webcam.")
args = ap.parse_args()

# -------- Sanity checks --------
if not MODEL_PATH.exists():
    sys.exit(f"[Error] Trained model not found at: {MODEL_PATH}")
if not CASCADE_PATH.exists():
    sys.exit(f"[Error] Haar cascade not found at: {CASCADE_PATH}")
if not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
    sys.exit("[Error] OpenCV contrib missing. Install: pip install opencv-contrib-python")

# -------- Load recognizer & cascade --------
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(str(MODEL_PATH))

face_cascade = cv2.CascadeClassifier(str(CASCADE_PATH))
if face_cascade.empty():
    sys.exit(f"[Error] Failed to load cascade: {CASCADE_PATH}")

# -------- Load label map (id -> name) --------
id_to_name = {}
if LABELMAP_PATH.exists():
    with open(LABELMAP_PATH, "r") as f:
        name_to_id = json.load(f)
    id_to_name = {int(v): k for k, v in name_to_id.items()}
else:
    print("[Warn] No label_map.json found; will display raw IDs.")

# -------- Drawing styles --------
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.6
FONT_COLOR = (255, 255, 255)
FONT_THICK = 2
TAG_BG = (0, 160, 0)    # green for accepted
TAG_H = 50
RECT_COLOR = (0, 255, 0)
RECT_THICK = 2

# -------- Detection params --------
SCALE_FACTOR = 1.1
MIN_NEIGHBORS = 5
MIN_SIZE = (50, 50)

def recognize_in_frame(frame, threshold, min_conf):
    """Detect and recognize faces on a single BGR frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.equalizeHist(gray, gray)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=SCALE_FACTOR,
        minNeighbors=MIN_NEIGHBORS,
        minSize=MIN_SIZE
    )

    accepted_count = 0
    for (x, y, w, h) in faces:
        roi = gray[y:y+h, x:x+w]
        roi = cv2.resize(roi, (200, 200), interpolation=cv2.INTER_LINEAR)
        cv2.equalizeHist(roi, roi)

        pred_id, dist = recognizer.predict(roi)
        conf_pct = max(0.0, min(100.0, 100.0 - (dist / threshold) * 100.0))

        # Only accept and draw if both conditions satisfied
        if dist <= threshold and conf_pct >= min_conf:
            accepted_count += 1
            name = id_to_name.get(pred_id, f"ID:{pred_id}")
            cv2.rectangle(frame, (x, y), (x + w, y + h), RECT_COLOR, RECT_THICK)

            top = max(0, y - TAG_H - 10)
            cv2.rectangle(frame, (x - 2, top), (x + w + 2, top + TAG_H), TAG_BG, -1)
            label = f"{name}: {conf_pct:.1f}% (d={dist:.1f})"
            cv2.putText(frame, label, (x + 4, top + TAG_H - 15),
                        FONT, FONT_SCALE, FONT_COLOR, FONT_THICK, cv2.LINE_AA)
    return frame, accepted_count

# -------- Single-image mode --------
if args.image:
    img_path = Path(args.image)
    if not img_path.exists():
        sys.exit(f"[Error] Image not found: {img_path}")
    frame = cv2.imread(str(img_path))
    if frame is None:
        sys.exit(f"[Error] Could not read image: {img_path}")

    out, nfaces = recognize_in_frame(frame, args.threshold, args.min_conf)
    cv2.putText(out, f"Accepted: {nfaces}", (10, 25),
                FONT, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.imshow(f"LBPH Predict - {img_path.name}", out)
    print(f"[info] Image: {img_path.name} | accepted faces: {nfaces} | thr={args.threshold} | minConf={args.min_conf}%")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    sys.exit(0)

# -------- Webcam mode --------
cap = cv2.VideoCapture(args.camera, cv2.CAP_AVFOUNDATION)
if not cap.isOpened():
    cap = cv2.VideoCapture(args.camera)
if not cap.isOpened():
    sys.exit("[Error] Could not open camera. Check permissions.")

prev = time.time(); fps = 0.0
while True:
    ok, frame = cap.read()
    if not ok:
        print("[Warn] Failed to read frame.")
        break

    out, nfaces = recognize_in_frame(frame, args.threshold, args.min_conf)
    now = time.time()
    fps = 0.9 * fps + 0.1 * (1.0 / max(1e-6, (now - prev))) if prev else 0.0
    prev = now
    hud = f"Accepted: {nfaces}  FPS: {fps:.1f}  thr={args.threshold:.0f}  minConf={args.min_conf:.0f}%"
    cv2.putText(out, hud, (10, 25), FONT, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow("Face Recognition (LBPH)", out)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()