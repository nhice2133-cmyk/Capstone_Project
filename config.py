"""
SMART ENTRY — Configuration
Centralizes all configurable parameters for the application.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # ── Flask ──────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "smart_entry_secret_2026_csucc")
    DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

    # ── Database ───────────────────────────────────────────────────────────
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "smart_entry.db")

    # ── Face Recognition ───────────────────────────────────────────────────
    # Haar Cascade classifier XML
    HAAR_CASCADE_PATH = os.path.join(
        BASE_DIR, "recognition", "haarcascade", "haarcascade_frontalface_default.xml"
    )
    # LBPH trained model file
    LBPH_MODEL_PATH = os.path.join(BASE_DIR, "recognition", "lbph_model.yml")

    # LBPH recognition confidence threshold.
    # A lower value is stricter (fewer false positives).
    # Recommended range: 60–90.  Default: 80.
    RECOGNITION_THRESHOLD = 80

    # Images to capture per user during enrollment
    ENROLLMENT_IMAGE_COUNT = 20

    # Face images storage (one sub-folder per user_id)
    FACE_DATA_DIR = os.path.join(BASE_DIR, "face_data")

    # Stranger alert snapshots
    ALERTS_SNAPSHOT_DIR = os.path.join(BASE_DIR, "static", "snapshots")

    # ── Camera ─────────────────────────────────────────────────────────────
    # Entry webcam index (usually 0 for the first USB webcam)
    ENTRY_CAMERA_INDEX = 0
    # Exit webcam index (usually 1 for the second USB webcam)
    EXIT_CAMERA_INDEX = 1

    # Frame resolution for face detection pipeline
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480

    # ── Detection Cooldowns ────────────────────────────────────────────────
    # Seconds to wait before a new alert is logged for the same unknown face
    ALERT_COOLDOWN_SECONDS = 10

    # Seconds to wait before recognizing the SAME student again on the SAME camera
    RECOGNITION_COOLDOWN_SECONDS = 60

    # ── Session ────────────────────────────────────────────────────────────
    # Minutes of inactivity before admin session expires
    SESSION_TIMEOUT_MINUTES = 30
