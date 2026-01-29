"""
Configuration module - Single source of truth for all paths and settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# API KEYS
# ============================================================
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
VOICE_ID = os.getenv("VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")  # Default voice

# ============================================================
# OUTPUT PATHS - Single clear structure
# ============================================================
AGENT_DIR = Path(__file__).parent.absolute()
OUTPUT_DIR = AGENT_DIR / "outputs" / "final"

# Create clean structure
VIDEO_OUTPUT_DIR = OUTPUT_DIR / "videos"
AUDIO_OUTPUT_DIR = OUTPUT_DIR / "audio"
IMAGE_OUTPUT_DIR = OUTPUT_DIR / "images"
TEMP_DIR = OUTPUT_DIR / "temp"

# Video settings
VIDEO_WIDTH = 854   # 480p width
VIDEO_HEIGHT = 480  # 480p height
VIDEO_FPS = 15

def init_output_dirs():
    """Create all output directories. Call once at startup."""
    for d in [OUTPUT_DIR, VIDEO_OUTPUT_DIR, AUDIO_OUTPUT_DIR, IMAGE_OUTPUT_DIR, TEMP_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR

def get_session_dir(session_id: str) -> Path:
    """Get session-specific output directory."""
    session_dir = OUTPUT_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "videos").mkdir(exist_ok=True)
    (session_dir / "audio").mkdir(exist_ok=True)
    (session_dir / "images").mkdir(exist_ok=True)
    (session_dir / "temp").mkdir(exist_ok=True)
    return session_dir

def cleanup_temp(session_dir: Path = None):
    """Clean up temporary files."""
    import shutil
    temp = (session_dir / "temp") if session_dir else TEMP_DIR
    if temp.exists():
        shutil.rmtree(temp, ignore_errors=True)
        temp.mkdir(exist_ok=True)
