import logging
import threading

from acquisition.recorder import recording_supervisor
from acquisition.monitor import monitor_stream

from config.camera_config import LOG_DIR


def main():

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(
                LOG_DIR / "acquisition.log"
            ),
            logging.StreamHandler()
        ]
    )

    stop_event = threading.Event()

    recorder_thread = threading.Thread(
        target=recording_supervisor,
        args=(stop_event,),
        name="Recorder",
        daemon=True
    )

    try:
        logging.info("Starting RTSP Acquisition Service")

        recorder_thread.start()

        monitor_stream(stop_event)

    except KeyboardInterrupt:
        logging.info("Shutdown requested")

    finally:
        stop_event.set()
        recorder_thread.join(timeout=15)

        logging.info("Acquisition service stopped")


if __name__ == "__main__":
    main()