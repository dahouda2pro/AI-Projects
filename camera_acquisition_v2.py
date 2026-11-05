
import cv2
import time
import logging

from config.camera_config import (
    RTSP_URL,
    RECONNECT_DELAY,
    MAX_FAILED_READS,
)


# ==================================================
# CONFIGURATION
# ==================================================

DISPLAY = True
FPS_LOG_INTERVAL = 5


# ==================================================
# LOGGING
# ==================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)


# ==================================================
# CAMERA CONNECTION
# ==================================================

def connect_camera():

    logging.info("Connecting to Avigilon IP camera...")

    cap = cv2.VideoCapture(
        RTSP_URL,
        cv2.CAP_FFMPEG
    )

    if not cap.isOpened():

        logging.error("Unable to open camera stream.")

        cap.release()

        return None

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    camera_fps = cap.get(cv2.CAP_PROP_FPS)

    logging.info("Camera connected successfully.")
    logging.info("Resolution: %s x %s", width, height)
    logging.info("Camera FPS: %.2f", camera_fps)

    return cap


# ==================================================
# CONTINUOUS FRAME ACQUISITION
# ==================================================

def run_acquisition():

    cap = None

    total_frames = 0
    failed_reads = 0

    start_time = time.monotonic()
    fps_start_time = start_time

    fps_frame_count = 0
    current_fps = 0.0

    logging.info("Starting continuous video acquisition.")

    try:

        while True:

            # ------------------------------------------
            # CONNECT / RECONNECT
            # ------------------------------------------

            if cap is None:

                cap = connect_camera()

                if cap is None:

                    logging.warning(
                        "Retrying connection in %s seconds...",
                        RECONNECT_DELAY
                    )

                    time.sleep(RECONNECT_DELAY)

                    continue

                failed_reads = 0
                fps_start_time = time.monotonic()
                fps_frame_count = 0

            # ------------------------------------------
            # READ CAMERA FRAME
            # ------------------------------------------

            ret, frame = cap.read()

            if not ret:

                failed_reads += 1

                if failed_reads >= MAX_FAILED_READS:

                    logging.warning(
                        "Camera stream interrupted. "
                        "Attempting reconnection..."
                    )

                    cap.release()
                    cap = None

                    failed_reads = 0

                    time.sleep(RECONNECT_DELAY)

                continue

            failed_reads = 0

            # ------------------------------------------
            # UPDATE FRAME COUNTERS
            # ------------------------------------------

            total_frames += 1
            fps_frame_count += 1

            now = time.monotonic()

            elapsed = now - fps_start_time

            # ------------------------------------------
            # CALCULATE ACQUISITION FPS
            # ------------------------------------------

            if elapsed >= FPS_LOG_INTERVAL:

                current_fps = fps_frame_count / elapsed

                logging.info(
                    "Frames received: %s | Acquisition FPS: %.2f",
                    total_frames,
                    current_fps
                )

                fps_frame_count = 0
                fps_start_time = now

            # ------------------------------------------
            # DISPLAY LIVE CAMERA
            # ------------------------------------------

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

                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):

                    logging.info(
                        "Acquisition stopped by user."
                    )

                    break

    except KeyboardInterrupt:

        logging.info("Acquisition interrupted by keyboard.")

    except Exception:

        logging.exception(
            "Unexpected acquisition error."
        )

    finally:

        # ----------------------------------------------
        # RELEASE RESOURCES
        # ----------------------------------------------

        if cap is not None:
            cap.release()

        cv2.destroyAllWindows()

        # ----------------------------------------------
        # ACQUISITION SUMMARY
        # ----------------------------------------------

        total_elapsed = time.monotonic() - start_time

        logging.info("=" * 50)
        logging.info("ACQUISITION SUMMARY")
        logging.info("Total frames: %s", total_frames)
        logging.info("Elapsed time: %.2f seconds", total_elapsed)

        if total_elapsed > 0:

            average_fps = total_frames / total_elapsed

            logging.info(
                "Average FPS: %.2f",
                average_fps
            )

        logging.info("Camera acquisition stopped.")
        logging.info("=" * 50)


# ==================================================
# APPLICATION ENTRY POINT
# ==================================================

if __name__ == "__main__":

    run_acquisition()
