#!/usr/bin/env python3
"""
Train LBPH (AI without ML) with optional simple validation.

Purpose
-------
- Load a face dataset (skipping any `.trash`).
- Infer labels robustly:
    1) Use parent folder name (preferred) if not 'dataset' or '.trash'.
    2) Else if filename matches `data.<LABEL>.<ts>.jpg`, use <LABEL>.
    3) Else if filename matches `<LABEL>_anything.ext`, use the prefix before the underscore.
- Detect the largest face per image (Haar), equalize histogram, resize to 200x200.
- Train an OpenCV LBPH recognizer (no epochs, no backprop).
- Optionally run a simple validation split to report accuracy and a confusion matrix.
- Save:
    - models/trained_lbph_face_recognizer_model.yml
    - models/label_map.json

Quick usage
-----------
# Train on all data (no validation)
python 03_train_model.py

# Recommended for practice and reporting (your chosen longest command):
python 03_train_model.py --val-split 0.2 --threshold 60

Notes
-----
- Threshold is only used in validation to decide when to label as 'Unknown'.
- Requires opencv-contrib-python for cv2.face.* APIs.
"""

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

# ---------- Paths ----------
ROOT = Path(__file__).resolve().parent
MODELS = ROOT / "models"
DATASET = ROOT / "dataset"
CASCADE = MODELS / "haarcascade_frontalface_default.xml"
MODEL_YML = MODELS / "trained_lbph_face_recognizer_model.yml"
LABELMAP = MODELS / "label_map.json"

# ---------- CLI ----------
ap = argparse.ArgumentParser(description="Train LBPH with optional simple validation.")
ap.add_argument("--val-split", type=float, default=0.0,
                help="Fraction per label for validation (e.g., 0.2).")
ap.add_argument("--threshold", type=float, default=80.0,
                help="Distance threshold for 'Unknown' during validation.")
ap.add_argument("--min-size", type=int, default=80,
                help="Min face size (pixels) for detection window.")
ap.add_argument("--unknown-csv", default="",
                help="If set, write Unknown validation samples to this CSV path.")
args = ap.parse_args()

# ---------- Checks ----------
if not CASCADE.exists():
    raise SystemExit(f"[Error] Cascade not found: {CASCADE}")
if not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
    raise SystemExit("[Error] Need opencv-contrib-python. Try: pip install opencv-contrib-python")

detector = cv2.CascadeClassifier(str(CASCADE))
if detector.empty():
    raise SystemExit(f"[Error] Failed to load cascade: {CASCADE}")

# ---------- Helpers ----------
def iter_images(folder: Path):
    """Yield image files under `folder`, excluding anything inside `.trash`."""
    exts = {".jpg", ".jpeg", ".png", ".bmp"}
    for p in sorted(folder.rglob("*")):
        if ".trash" in p.parts:
            continue
        if p.is_file() and p.suffix.lower() in exts and not p.name.startswith("."):
            yield p

def label_from_name(p: Path):
    """
    Robust label extraction:
      1) If parent folder is a person's name (and not 'dataset' or '.trash'), use it.
      2) If filename looks like data.<LABEL>.<ts>.jpg, use <LABEL>.
      3) If filename looks like <LABEL>_anything.ext, use <LABEL>.
      Returns None if no label can be inferred.
    """
    parent = p.parent.name
    if parent not in ('.trash', 'dataset'):
        return parent

    parts = p.name.split(".")
    if len(parts) > 2 and parts[0].lower() == "data":
        return parts[1]

    stem = p.stem
    if "_" in stem:
        return stem.split("_", 1)[0]

    return None

def load_data(ds: Path, min_size: int):
    """
    Load images, detect largest face (if any), equalize, resize (200x200).
    Returns:
      faces: List[np.ndarray of shape (200,200)]
      labels: List[str] human-readable labels
      paths: List[str] source file paths
    """
    faces, labels, paths = [], [], []
    for imgp in iter_images(ds):
        lbl = label_from_name(imgp)
        if not lbl:
            continue
        try:
            # Grayscale + histogram equalization
            g = np.array(Image.open(imgp).convert("L"), dtype="uint8")
            g = cv2.equalizeHist(g)

            # Detect face region
            rects = detector.detectMultiScale(
                g, scaleFactor=1.2, minNeighbors=5, minSize=(min_size, min_size)
            )
            if len(rects):
                x, y, w, h = max(rects, key=lambda r: r[2] * r[3])  # largest face
                roi = g[y:y+h, x:x+w]
            else:
                roi = g  # fallback: some datasets are already cropped faces

            roi = cv2.resize(roi, (200, 200), interpolation=cv2.INTER_LINEAR)
            faces.append(roi)
            labels.append(lbl)
            paths.append(str(imgp))
        except Exception as e:
            print(f"[Warn] skip {imgp}: {e}")
    return faces, labels, paths

def encode_labels(names):
    """Map string labels to integer IDs, return ids-array and mapping dict."""
    uniq = sorted(set(names))
    name_to_id = {n: i for i, n in enumerate(uniq)}
    ids = np.array([name_to_id[n] for n in names], np.int32)
    return ids, name_to_id

def stratified_split(ids, frac):
    """Split indices per class to keep class balance."""
    by = defaultdict(list)
    for i, l in enumerate(ids):
        by[int(l)].append(i)
    tr, va = [], []
    for l, idxs in by.items():
        idxs = idxs[:]
        random.shuffle(idxs)
        n_val = int(len(idxs) * frac)
        va += idxs[:n_val]; tr += idxs[n_val:]
    return tr, va

def train_lbph(faces, ids, idxs):
    """Create and train an LBPH recognizer on the given indices."""
    recog = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
    X = [faces[i] for i in idxs]
    y = np.array([ids[i] for i in idxs], np.int32)
    recog.train(X, y)
    return recog

def simple_eval(recog, faces, ids, paths, threshold, num_labels):
    """
    Evaluate on a validation set using a fixed distance threshold.
    Confusion matrix last column is 'Unknown' (dist > threshold).
    """
    unknown = num_labels
    cm = np.zeros((num_labels, num_labels + 1), dtype=int)
    total = len(faces); correct = 0; unk = 0
    unk_rows = []

    for img, true_id, pth in zip(faces, ids, paths):
        pred_id, dist = recog.predict(img)
        if dist > threshold:
            cm[true_id, unknown] += 1
            unk += 1
            unk_rows.append((pth, dist))
        else:
            cm[true_id, pred_id] += 1
            if pred_id == true_id:
                correct += 1

    acc = correct / total if total else 0.0
    return acc, unk, cm, unk_rows

def print_confusion(cm, id_to_name):
    """Pretty-print a confusion matrix with 'Unknown' as the last column."""
    names = [id_to_name[i] for i in range(len(id_to_name))]
    print("\nConfusion matrix (rows=true, cols=pred, last col=Unknown):")
    header = ["true\\pred"] + names + ["Unknown"]
    colw = max(8, max(len(h) for h in header))
    print(" ".join(h.ljust(colw) for h in header))
    for i, row in enumerate(cm):
        cells = [names[i].ljust(colw)] + [str(v).ljust(colw) for v in row]
        print(" ".join(cells))

# ---------- Main ----------
def main():
    random.seed(42)
    if not DATASET.exists():
        raise SystemExit(f"[Error] Dataset not found: {DATASET}")

    # Load all usable samples (skips .trash; robust labels)
    faces, names, paths = load_data(DATASET, args.min_size)
    print(f"[info] loaded {len(faces)} samples from {DATASET}")
    if faces:
        c = Counter(names)
        print("[info] per-label counts:", dict(c))
    else:
        raise SystemExit("[Error] No usable images.")

    # Encode labels
    ids, name_to_id = encode_labels(names)
    id_to_name = {v: k for k, v in name_to_id.items()}

    # Train (with or without validation)
    if args.val_split > 0:
        tr_idx, va_idx = stratified_split(ids, args.val_split)
        recog = train_lbph(faces, ids, tr_idx)

        # Build validation subsets
        Xv = [faces[i] for i in va_idx]
        yv = [int(ids[i]) for i in va_idx]
        pv = [paths[i] for i in va_idx]

        acc, unk_count, cm, unk_rows = simple_eval(
            recog, Xv, yv, pv, args.threshold, len(name_to_id)
        )

        # ---- Educational validation summary for beginners ----
        total_samples = len(faces)
        val_count = len(Xv)
        train_count = len(tr_idx)
        print("\n------------------ Validation Summary ------------------")
        print(f"Total dataset size : {total_samples} image(s)")
        print(f"Validation split   : {args.val_split*100:.0f}%  →  {val_count} image(s) used for testing")
        print(f"Training set size  : {train_count} image(s)")
        print(f"Threshold distance : {args.threshold} (faces with distance > {args.threshold} are 'Unknown')")
        print("--------------------------------------------------------")

        # ---- Actual results ----
        print(f"\n[VAL] acc={acc:.3f}  (threshold={args.threshold})   n={val_count}")
        print(f"[VAL] Unknown (rejected): {unk_count}")
        print_confusion(cm, id_to_name)

        if args.unknown_csv and unk_rows:
            out = Path(args.unknown_csv); out.parent.mkdir(parents=True, exist_ok=True)
            with open(out, "w", newline="") as f:
                w = csv.writer(f); w.writerow(["path", "dist"])
                for p, d in unk_rows:
                    w.writerow([p, f"{d:.3f}"])
            print(f"[OK] Unknown list → {out}")

        # Save model trained on train split
        MODELS.mkdir(parents=True, exist_ok=True)
        recog.save(str(MODEL_YML))
    else:
        # Train on ALL data (no validation metrics)
        recog = train_lbph(faces, ids, list(range(len(faces))))
        MODELS.mkdir(parents=True, exist_ok=True)
        recog.save(str(MODEL_YML))

    # Save label map
    with open(LABELMAP, "w") as f:
        json.dump(name_to_id, f, indent=2)

    print(f"\n[OK] Model → {MODEL_YML}")
    print(f"[OK] Label map → {LABELMAP}")
    print("     Labels:", ", ".join(f"{k}:{v}" for k, v in name_to_id.items()))

if __name__ == "__main__":
    main()