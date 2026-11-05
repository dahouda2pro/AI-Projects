
import os
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# Camera settings
CAMERA_USERNAME = os.getenv("CAMERA_USERNAME")
CAMERA_PASSWORD = os.getenv("CAMERA_PASSWORD")
CAMERA_IP = os.getenv("CAMERA_IP")
CAMERA_PORT = os.getenv("CAMERA_PORT", "554")
CAMERA_RTSP_PATH = os.getenv("CAMERA_RTSP_PATH")

if not all([
    CAMERA_USERNAME,
    CAMERA_PASSWORD,
    CAMERA_IP,
    CAMERA_RTSP_PATH
]):
    raise ValueError("Missing camera configuration in .env")

# Build RTSP URL
username = quote(CAMERA_USERNAME, safe="")
password = quote(CAMERA_PASSWORD, safe="")

RTSP_URL = (
    f"rtsp://{username}:{password}"
    f"@{CAMERA_IP}:{CAMERA_PORT}"
    f"{CAMERA_RTSP_PATH}"
)

# Directories
RECORDINGS_DIR = BASE_DIR / "recordings"
LOGS_DIR = BASE_DIR / "logs"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Acquisition settings
RECONNECT_DELAY = 5
MAX_FAILED_READS = 10

# Recording settings
SEGMENT_DURATION = 300

# Create directories
for directory in [
    RECORDINGS_DIR,
    LOGS_DIR,
    OUTPUTS_DIR
]:
    directory.mkdir(parents=True, exist_ok=True)
