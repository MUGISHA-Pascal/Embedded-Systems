#!/usr/bin/env python3
"""
Dataset Preview and Cleaner (LBPH project, beginner-friendly)

Purpose
-------
Visually browse and curate your face dataset. You can:
- Preview images in a consistent 1280×720 window with a simple HUD.
- Navigate manually or play a slideshow.
- Delete images **permanently** (no trash, no undo).

Notes
-----
- Deletion is immediate and irreversible from within this tool.
- If you need a reversible flow, use version control (git) or keep backups.

Controls
--------
n       : next image
p      : previous image
space / s   : play/pause slideshow
+ or =      : faster slideshow
- or _      : slower slideshow
d           : delete current image (PERMANENT)
q or ESC    : quit
"""

import cv2, time
from pathlib import Path
import numpy as np

# --- Auto-clean any leftover .trash directories (from older versions) ---
from shutil import rmtree

for trash_dir in Path("dataset").rglob(".trash"):
    try:
        rmtree(trash_dir, ignore_errors=True)
        print(f"[cleanup] Removed old trash folder: {trash_dir}")
    except Exception as e:
        print(f"[warn] Could not remove {trash_dir}: {e}")
        
def preview(folder="dataset", pattern="*.jpg", delay_ms=1000):
    """Main preview function: renders images with a HUD and supports curation actions."""
    folder = Path(folder)

    # -------- Gather all valid image paths recursively --------
    files = sorted(
        f for f in folder.rglob(pattern)
        if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp")
        and not f.name.startswith(".")
    )
    if not files:
        print(f"No images found in '{folder}'")
        return

    # -------- Window/HUD geometry (fixed layout for consistency) --------
    win = "Preview"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)

    FRAME_W, FRAME_H = 1280, 720
    TOP_BAR_H, BOTTOM_BAR_H = 55, 55
    VIEW_X, VIEW_Y = 0, TOP_BAR_H
    VIEW_W, VIEW_H = FRAME_W, FRAME_H - TOP_BAR_H - BOTTOM_BAR_H

    FONT = cv2.FONT_HERSHEY_SIMPLEX
    FONT_SCALE_TOP, FONT_SCALE_BOTTOM = 0.8, 0.65
    THICK_TOP, THICK_BOTTOM = 2, 2
    GREEN = (0, 180, 0)      # BGR
    WHITE = (255, 255, 255)
    PAD_X, PAD_Y = 20, 15

    # -------- Flash notification state --------
    FLASH_TS = 0.0      # last time we flashed a notification
    FLASH_MS = 400      # flash duration (ms)
    FLASH_TEXT = ""     # "Deleted" or other status messages

    # ---------- Helpers ----------

    def truncate_to_width(text, max_w, font, scale, thick):
        """Truncate 'text' so it fits within 'max_w' pixels (adds a mid-ellipsis)."""
        (tw, _), _ = cv2.getTextSize(text, font, scale, thick)
        if tw <= max_w:
            return text
        if len(text) <= 4:
            return text[:1] + "…"
        left, right = 0, len(text)
        base = text
        while left + 2 < right - 2:
            candidate = base[:2 + left] + "…" + base[-(2 + left):]
            (cw, _), _ = cv2.getTextSize(candidate, font, scale, thick)
            if cw > max_w:
                left += 1
            else:
                right -= 1
        return base[:2 + left] + "…" + base[-(2 + left):]

    def delete_current(img_path: Path):
        """Permanently delete the current image (no trash, no undo)."""
        nonlocal FLASH_TS, FLASH_TEXT
        try:
            img_path.unlink(missing_ok=True)  # permanent delete
            FLASH_TEXT = "Deleted permanently"
            FLASH_TS = time.time()
            print(f"[deleted] {img_path}")
            return True
        except Exception as e:
            FLASH_TEXT = "Delete failed"
            FLASH_TS = time.time()
            print(f"[error] Could not delete {img_path}: {e}")
            return False

    def draw_flash(frame):
        """Draw a small green pill notification in the top bar."""
        if (time.time() - FLASH_TS) * 1000 <= FLASH_MS and FLASH_TEXT:
            text = FLASH_TEXT
            (tw, th), _ = cv2.getTextSize(text, FONT, 0.65, 2)
            x1, y1 = FRAME_W - PAD_X - tw - 24, 8
            x2, y2 = FRAME_W - PAD_X, 8 + th + 18
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 160, 0), -1)
            cv2.putText(frame, text, (x1 + 12, y2 - 8), FONT, 0.65, WHITE, 2, cv2.LINE_AA)

    def draw_frame(img_path, autoplay, delay, idx):
        """Compose the 1280×720 viewing frame with letterboxed image + HUD."""
        frame = np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8)

        # ---- Load and letterbox into the view area ----
        img = cv2.imread(str(img_path))
        if img is not None and img.size > 0:
            ih, iw = img.shape[:2]
            scale = min(VIEW_W / iw, VIEW_H / ih)
            new_w, new_h = max(1, int(iw * scale)), max(1, int(ih * scale))
            resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            off_x = VIEW_X + (VIEW_W - new_w) // 2
            off_y = VIEW_Y + (VIEW_H - new_h) // 2
            frame[off_y:off_y+new_h, off_x:off_x+new_w] = resized

        # ---- Top green bar: index, filename, and state ----
        cv2.rectangle(frame, (0, 0), (FRAME_W, TOP_BAR_H), GREEN, -1)
        left_text = f"[{idx+1}/{len(files)}] "
        state_text = f"  |  {'PLAY' if autoplay else 'PAUSE'}  |  delay={delay}ms"
        max_name_w = FRAME_W - 2*PAD_X - cv2.getTextSize(left_text + state_text, FONT, FONT_SCALE_TOP, THICK_TOP)[0][0]
        name = truncate_to_width(img_path.name, max_name_w, FONT, FONT_SCALE_TOP, THICK_TOP)
        top_text = f"{left_text}{name}{state_text}"
        cv2.putText(frame, top_text, (PAD_X, TOP_BAR_H - PAD_Y),
                    FONT, FONT_SCALE_TOP, WHITE, THICK_TOP, cv2.LINE_AA)

        # ---- Bottom green bar: control hints ----
        cv2.rectangle(frame, (0, FRAME_H - BOTTOM_BAR_H), (FRAME_W, FRAME_H), GREEN, -1)
        help_text = "p: prev   n: next   space/s: pause/resume   +/- speed   d: DELETE (PERMANENT)   q/ESC: quit"
        cv2.putText(frame, help_text, (PAD_X, FRAME_H - PAD_Y),
                    FONT, FONT_SCALE_BOTTOM, WHITE, THICK_BOTTOM, cv2.LINE_AA)

        # ---- Flash notifications (Deleted permanently / Delete failed) ----
        draw_flash(frame)
        return frame

    # -------- Main event loop --------
    idx = 0
    autoplay = False
    last = time.time()

    while True:
        # Draw current frame (or empty message if list is empty)
        if not files:
            blank = np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8)
            cv2.rectangle(blank, (0, 0), (FRAME_W, TOP_BAR_H), GREEN, -1)
            cv2.putText(blank, "No images left. Press q to exit.",
                        (PAD_X, TOP_BAR_H - PAD_Y), FONT, 0.8, WHITE, 2, cv2.LINE_AA)
            cv2.imshow(win, blank)
        else:
            out = draw_frame(files[idx], autoplay, delay_ms, idx)
            cv2.imshow(win, out)

        # Auto-advance in slideshow mode
        if files and autoplay and (time.time() - last) * 1000 >= delay_ms:
            idx = (idx + 1) % len(files)
            last = time.time()

        # Handle key events (use waitKeyEx to disambiguate arrows)
        key = cv2.waitKeyEx(30)

        # Arrow key constants (from waitKeyEx)
        KEY_LEFT  = 2424832
        KEY_RIGHT = 2555904

        if key == -1:
            continue

        # Quit: lowercase 'q', uppercase 'Q', or ESC
        if key in (ord('q'), ord('Q'), 27):
            break

        # Next / Prev (support both arrow keys and n/p)
        elif files and (key in (KEY_RIGHT, ord('n'), ord('N'))):
            idx = (idx + 1) % len(files)
            last = time.time()
        elif files and (key in (KEY_LEFT, ord('p'), ord('P'))):
            idx = (idx - 1) % len(files)
            last = time.time()

        # Toggle slideshow
        elif key in (ord(' '), ord('s'), ord('S')):
            autoplay = not autoplay
            last = time.time()

        # Speed control
        elif key in (ord('+'), ord('=')):
            delay_ms = max(50, int(delay_ms * 0.8))
        elif key in (ord('-'), ord('_')):
            delay_ms = min(5000, int(delay_ms * 1.25))

        # Delete permanently
        elif files and key in (ord('d'), ord('D')):
            to_delete = files[idx]
            if delete_current(to_delete):
                # Remove from in-memory list and keep index valid
                try:
                    files.pop(idx)
                except Exception:
                    pass
                if files:
                    idx %= len(files)

    cv2.destroyAllWindows()


# ---------- Entry point ----------
if __name__ == "__main__":
    # Default: preview all .jpg in 'dataset' with a 250 ms slideshow delay
    preview(folder="dataset", pattern="*.jpg", delay_ms=250)