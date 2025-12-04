"""
Face Mesh Detection Application
Uses MediaPipe to detect and visualize 468 facial landmarks in real-time
No ML training required - uses pre-trained models
"""
import cv2
import mediapipe as mp
import numpy as np
import time
from datetime import datetime
class FaceMeshDetector:
    def __init__(self, static_mode=False, max_faces=2, refine_landmarks=True,
                 min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        Initialize Face Mesh Detector
        Args:
            static_mode: Whether to treat input as static images or video stream
            max_faces: Maximum number of faces to detect
            refine_landmarks: Whether to refine landmarks around eyes and lips
            min_detection_confidence: Minimum confidence for face detection
            min_tracking_confidence: Minimum confidence for face tracking
        """
        self.static_mode = static_mode
        self.max_faces = max_faces
        self.refine_landmarks = refine_landmarks
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=self.static_mode,
            max_num_faces=self.max_faces,
            refine_landmarks=self.refine_landmarks,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        # Visualization modes
        self.show_tesselation = True
        self.show_contours = True
        self.show_irises = True
    def find_face_mesh(self, img, draw=True):
        """
        Detect face mesh in an image
        Args:
            img: Input image (BGR format)
            draw: Whether to draw the mesh on the image
        Returns:
            img: Image with face mesh drawn (if draw=True)
            faces: List of detected faces with landmark coordinates
        """
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Process image
        results = self.face_mesh.process(img_rgb)
        faces = []
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                if draw:
                    # Draw tesselation (mesh connections)
                    if self.show_tesselation:
                        self.mp_drawing.draw_landmarks(
                            image=img,
                            landmark_list=face_landmarks,
                            connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
                        )
                    # Draw contours (face outline)
                    if self.show_contours:
                        self.mp_drawing.draw_landmarks(
                            image=img,
                            landmark_list=face_landmarks,
                            connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
                        )
                    # Draw irises
                    if self.show_irises:
                        self.mp_drawing.draw_landmarks(
                            image=img,
                            landmark_list=face_landmarks,
                            connections=self.mp_face_mesh.FACEMESH_IRISES,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_iris_connections_style()
                        )
                # Extract landmark coordinates
                face = []
                h, w, c = img.shape
                for id, lm in enumerate(face_landmarks.landmark):
                    x, y = int(lm.x * w), int(lm.y * h)
                    face.append([id, x, y])
                faces.append(face)
        return img, faces
    def toggle_tesselation(self):
        """Toggle tesselation display"""
        self.show_tesselation = not self.show_tesselation
    def toggle_contours(self):
        """Toggle contours display"""
        self.show_contours = not self.show_contours
    def toggle_irises(self):
        """Toggle irises display"""
        self.show_irises = not self.show_irises
def main():
    """Main function to run face mesh detection"""
    print("=" * 60)
    print("Face Mesh Detection - AI without ML Part 2")
    print("=" * 60)
    print("\nInitializing webcam and face mesh detector...")
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open webcam!")
        print("Please check if your camera is connected and not being used by another application.")
        return
    # Set camera resolution for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    # Initialize detector
    detector = FaceMeshDetector(
        static_mode=False,
        max_faces=2,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    # FPS tracking
    prev_time = 0
    print("\n✓ Initialization complete!")
    print("\nKEYBOARD CONTROLS:")
    print("  T - Toggle Tesselation (mesh lines)")
    print("  C - Toggle Contours (face outline)")
    print("  I - Toggle Irises (eye tracking)")
    print("  S - Save screenshot")
    print("  Q or ESC - Quit")
    print("\nStarting face mesh detection...\n")
    while True:
        success, img = cap.read()
        if not success:
            print("WARNING: Failed to read frame from webcam")
            continue
        # Flip image for selfie view
        img = cv2.flip(img, 1)
        # Detect face mesh
        img, faces = detector.find_face_mesh(img, draw=True)
        # Calculate FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
        prev_time = curr_time
        # Display information
        h, w, c = img.shape
        # Semi-transparent overlay for text background
        overlay = img.copy()
        cv2.rectangle(overlay, (10, 10), (400, 150), (0, 0, 0), -1)
        img = cv2.addWeighted(overlay, 0.3, img, 0.7, 0)
        # Display FPS
        cv2.putText(img, f'FPS: {int(fps)}', (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # Display number of faces detected
        num_faces = len(faces)
        color = (0, 255, 0) if num_faces > 0 else (0, 0, 255)
        cv2.putText(img, f'Faces Detected: {num_faces}', (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        # Display current visualization modes
        mode_text = []
        if detector.show_tesselation:
            mode_text.append("Tesselation")
        if detector.show_contours:
            mode_text.append("Contours")
        if detector.show_irises:
            mode_text.append("Irises")
        modes = " | ".join(mode_text) if mode_text else "None"
        cv2.putText(img, f'Modes: {modes}', (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        # Display controls hint
        cv2.putText(img, 'Press Q to quit, S to screenshot', (20, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        # Show image
        cv2.imshow('Face Mesh Detection', img)
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # Q or ESC
            print("\nExiting...")
            break
        elif key == ord('t'):  # Toggle tesselation
            detector.toggle_tesselation()
            status = "ON" if detector.show_tesselation else "OFF"
            print(f"Tesselation: {status}")
        elif key == ord('c'):  # Toggle contours
            detector.toggle_contours()
            status = "ON" if detector.show_contours else "OFF"
            print(f"Contours: {status}")
        elif key == ord('i'):  # Toggle irises
            detector.toggle_irises()
            status = "ON" if detector.show_irises else "OFF"
            print(f"Irises: {status}")
        elif key == ord('s'):  # Save screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"facemesh_screenshot_{timestamp}.png"
            cv2.imwrite(filename, img)
            print(f"Screenshot saved: {filename}")
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("\n✓ Application closed successfully")
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("\nMake sure you have installed all required packages:")
        print("  pip install -r requirements.txt")









