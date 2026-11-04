import subprocess
import time
import logging
from datetime import datetime, timedelta

from config.camera_config import (
    RTSP_URL,
    RECORDINGS_DIR,
    SEGMENT_DURATION,
    RECONNECT_DELAY,
)


def seconds_until_midnight():
    now = datetime.now()
    tomorrow = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return max(1, int((tomorrow - now).total_seconds()))


def recording_supervisor(stop_event):

    while not stop_event.is_set():

        today = datetime.now()
        output_dir = (
            RECORDINGS_DIR
            / today.strftime("%Y")
            / today.strftime("%m")
            / today.strftime("%d")
        )

        output_dir.mkdir(parents=True, exist_ok=True)

        output_pattern = str(
            output_dir / "traffic_%H%M%S.mp4"
        )

        duration = seconds_until_midnight()

        command = [
            "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-loglevel", "warning",
            "-rtsp_transport", "tcp",
            "-i", RTSP_URL,
            "-map", "0:v:0",
            "-c:v", "copy",
            "-an",
            "-t", str(duration),
            "-f", "segment",
            "-segment_time", str(SEGMENT_DURATION),
            "-reset_timestamps", "1",
            "-strftime", "1",
            output_pattern,
        ]

        process = None

        try:
            logging.info("Starting FFmpeg recorder")

            process = subprocess.Popen(command)

            while process.poll() is None:

                if stop_event.wait(1):
                    process.terminate()

                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()

                    break

            if not stop_event.is_set():
                logging.warning(
                    "FFmpeg stopped. Exit code: %s",
                    process.returncode
                )

        except Exception:
            logging.exception("Recording service error")

        finally:
            if process and process.poll() is None:
                process.terminate()
                process.wait()

        if not stop_event.is_set():
            logging.info(
                "Restarting recorder in %s seconds",
                RECONNECT_DELAY
            )
            stop_event.wait(RECONNECT_DELAY)

    logging.info("Recording supervisor stopped")