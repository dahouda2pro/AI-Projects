import subprocess
import logging
from pathlib import Path
from datetime import datetime

from config.camera_config import RTSP_URL

# ==========================================
# CONFIGURATION
# ==========================================

FFMPEG = "ffmpeg"
SEGMENT_DURATION = 300  # 5 minutes

BASE_DIR = Path(__file__).resolve().parent
RECORDINGS_DIR = BASE_DIR / "recordings"

today = datetime.now().strftime("%Y-%m-%d")
output_dir = RECORDINGS_DIR / today
output_dir.mkdir(parents=True, exist_ok=True)

# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ==========================================
# RECORDING
# ==========================================

def start_recording():

    output_pattern = str(
        output_dir / "camera_%Y%m%d_%H%M%S.mp4"
    )

    command = [
        FFMPEG,
        "-hide_banner",
        "-rtsp_transport", "tcp",
        "-i", RTSP_URL,
        "-map", "0:v:0",
        "-an",
        "-c:v", "copy",
        "-f", "segment",
        "-segment_time", str(SEGMENT_DURATION),
        "-reset_timestamps", "1",
        "-strftime", "1",
        "-segment_format_options", "movflags=+faststart",
        output_pattern
    ]

    logging.info("Starting camera recording...")
    logging.info("Output directory: %s", output_dir)
    logging.info("Segment duration: %s seconds", SEGMENT_DURATION)

    try:
        subprocess.run(command, check=True)

    except FileNotFoundError:
        logging.error("FFmpeg executable not found. Check PATH.")

    except subprocess.CalledProcessError as error:
        logging.error("FFmpeg stopped with error: %s", error)

    except KeyboardInterrupt:
        logging.info("Recording interrupted by user.")


if __name__ == "__main__":
    start_recording()
