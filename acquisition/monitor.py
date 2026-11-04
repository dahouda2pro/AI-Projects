import cv2
import time
import logging

from config.camera_config import (
    RTSP_URL,
    DISPLAY,
    RECONNECT_DELAY,
    MONITOR_INTERVAL,
)


def monitor_stream(stop_event):

    while not stop_event.is_set():

        cap = None

        try:
            logging.info("Connecting to RTSP stream")

            cap = cv2.VideoCapture(
                RTSP_URL,
                cv2.CAP_FFMPEG
            )

            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if not cap.isOpened():
                logging.error("RTSP connection failed")
                stop_event.wait(RECONNECT_DELAY)
                continue

            logging.info("RTSP connection established")

            frame_count = 0
            window_frames = 0
            window_start = time.time()

            while not stop_event.is_set():

                ret, frame = cap.read()

                if not ret:
                    logging.warning("Frame acquisition failed")
                    break

                frame_count += 1
                window_frames += 1

                if DISPLAY:
                    cv2.imshow("RTSP Monitor", frame)

                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        stop_event.set()
                        break

                elapsed = time.time() - window_start

                if elapsed >= MONITOR_INTERVAL:
                    fps = window_frames / elapsed

                    logging.info(
                        "Frames=%s | FPS=%.2f | Resolution=%sx%s",
                        frame_count,
                        fps,
                        frame.shape[1],
                        frame.shape[0]
                    )

                    window_frames = 0
                    window_start = time.time()

        except Exception:
            logging.exception("Monitoring service error")

        finally:
            if cap is not None:
                cap.release()

            if DISPLAY:
                cv2.destroyAllWindows()

        if not stop_event.is_set():
            logging.info("Reconnecting in %s seconds", RECONNECT_DELAY)
            stop_event.wait(RECONNECT_DELAY)

    logging.info("Monitoring service stopped")