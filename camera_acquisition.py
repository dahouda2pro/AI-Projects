
import os
import cv2
import time
import logging

from dotenv import load_dotenv
from urllib.parse import quote

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

username = quote(os.getenv("CAMERA_USERNAME", ""), safe="")
password = quote(os.getenv("CAMERA_PASSWORD", ""), safe="")

camera_ip = os.getenv("CAMERA_IP")
camera_port = os.getenv("CAMERA_PORT", "554")
stream_path = os.getenv("CAMERA_RTSP_PATH")

if not all([username, password, camera_ip, stream_path]):
    raise ValueError("Missing camera configuration in .env")

RTSP_URL = (
    f"rtsp://{username}:{password}"
    f"@{camera_ip}:{camera_port}{stream_path}"
)

RECONNECT_DELAY = 5
MAX_FAILED_READS = 10
DISPLAY = True

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
    "rtsp_transport;tcp"
)

# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# --------------------------------------------------
# CAMERA CONNECTION
# --------------------------------------------------

def connect_camera():

    logging.info("Connecting to Avigilon camera...")

    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

    if cap.isOpened():
        logging.info("Camera connected successfully.")
        logging.info(
            "Resolution: %s x %s",
            int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        )
        return cap

    cap.release()

    logging.error("Unable to connect to camera.")

    return None


# --------------------------------------------------
# CONTINUOUS FRAME ACQUISITION
# --------------------------------------------------

def run_acquisition():

    cap = None

    total_frames = 0
    failed_reads = 0

    start_time = time.monotonic()
    fps_start_time = start_time
    fps_frame_count = 0

    current_fps = 0.0

    try:

        while True:

            # Connect or reconnect
            if cap is None:

                cap = connect_camera()

                if cap is None:
                    logging.warning(
                        "Retrying in %s seconds...",
                        RECONNECT_DELAY
                    )
                    time.sleep(RECONNECT_DELAY)
                    continue

                failed_reads = 0

            # Read camera frame
            ret, frame = cap.read()

            if not ret:

                failed_reads += 1

                if failed_reads >= MAX_FAILED_READS:

                    logging.warning(
                        "Camera stream interrupted. Reconnecting..."
                    )

                    cap.release()
                    cap = None

                    time.sleep(RECONNECT_DELAY)

                continue

            failed_reads = 0

            total_frames += 1
            fps_frame_count += 1

            now = time.monotonic()

            # Calculate actual acquisition FPS every 5 seconds
            elapsed = now - fps_start_time

            if elapsed >= 5:

                current_fps = fps_frame_count / elapsed

                logging.info(
                    "Frames received: %s | Acquisition FPS: %.2f",
                    total_frames,
                    current_fps
                )

                fps_frame_count = 0
                fps_start_time = now

            # Display live camera with acquisition information
            if DISPLAY:

                display_frame = frame.copy()

                cv2.putText(
                    display_frame,
                    f"Frames: {total_frames}",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    display_frame,
                    f"FPS: {current_fps:.2f}",
                    (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                cv2.imshow(
                    "Avigilon - Continuous Acquisition",
                    display_frame
                )

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logging.info("Acquisition stopped by user.")
                    break

    except KeyboardInterrupt:
        logging.info("Acquisition interrupted.")

    except Exception:
        logging.exception("Acquisition error.")

    finally:

        if cap is not None:
            cap.release()

        cv2.destroyAllWindows()

        total_elapsed = time.monotonic() - start_time

        logging.info("--------------------------------")
        logging.info("ACQUISITION SUMMARY")
        logging.info("Total frames: %s", total_frames)
        logging.info("Elapsed time: %.2f seconds", total_elapsed)

        if total_elapsed > 0:
            logging.info(
                "Average FPS: %.2f",
                total_frames / total_elapsed
            )

        logging.info("Camera acquisition stopped.")


if __name__ == "__main__":
    run_acquisition()
