import os
from pathlib import Path

class Settings:
    GEMINI_API_KEY     = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL       = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")
    TTS_VOICE          = os.environ.get("TTS_VOICE", "af_heart")
    TTS_SPEED          = float(os.environ.get("TTS_SPEED", "1.0"))
    TTS_LANGUAGE       = os.environ.get("TTS_LANGUAGE", "en-us")
    FRAME_SAMPLE_RATE  = int(os.environ.get("FRAME_SAMPLE_RATE", "10"))
    MAX_VIDEO_SIZE_MB  = 500
    
    # Paths (Colab paths වෙනුවට relative paths පාවිච්චි කර ඇත)
    BASE_DIR   = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR = BASE_DIR / "uploads"
    OUTPUT_DIR = BASE_DIR / "outputs"
    TEMP_DIR   = BASE_DIR / "temp"

settings = Settings()