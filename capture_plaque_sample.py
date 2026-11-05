
import cv2
from pathlib import Path

from config.camera_config import RTSP_URL

OUTPUT_DIR = Path("outputs/plate_samples")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

if not cap.isOpened():
    raise RuntimeError("Cannot connect to Avigilon camera")

print("Camera connected. Press S to save a frame, Q to quit.")

try:
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Unable to read frame")
            continue

        cv2.imshow("Avigilon - Plate Sample Capture", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            output = OUTPUT_DIR / "camera_sample.jpg"
            cv2.imwrite(str(output), frame)
            print(f"Frame saved: {output}")

        elif key == ord("q"):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
