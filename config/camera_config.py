from pathlib import Path

BASE_DIR = Path("/home/anyaccess/dmwamba2-t1/dx/RTSP_TEST/Test_RTSPLink_v1/")

# RTSP source
RTSP_URL = "rtsp://127.0.0.1:8554/traffic"

# Storage
RECORDINGS_DIR = BASE_DIR / "recordings"
LOG_DIR = BASE_DIR / "logs"

# Recording
SEGMENT_DURATION = 300  # 5 minutes
VIDEO_CODEC = "copy"

# Monitoring
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
DISPLAY = False

# Recovery
RECONNECT_DELAY = 5
MONITOR_INTERVAL = 300