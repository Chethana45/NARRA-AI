"""
Centralized configuration for NARRA.AI backend.

Reads all secrets/config from environment variables (populated from a local
.env file via python-dotenv). NEVER hard-code API keys or credentials here.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Load .env from the backend directory if present. This file is gitignored
# and must be created locally by whoever runs the app; it is never committed.
load_dotenv(BASE_DIR / ".env")


def _get_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


# --- Gemini (Google AI Studio) ---
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_VISION_MODEL: str = os.getenv("GEMINI_VISION_MODEL", "gemini-2.0-flash")
GEMINI_TEXT_MODEL: str = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.0-flash")
GEMINI_API_BASE: str = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_TIMEOUT_SECONDS: float = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "45"))

# Whether Gemini is actually configured/usable.
GEMINI_ENABLED: bool = bool(GEMINI_API_KEY)

# --- Research (Wikipedia / Wikidata, no API key required) ---
WIKIPEDIA_API_BASE: str = "https://en.wikipedia.org/w"
WIKIPEDIA_REST_BASE: str = "https://en.wikipedia.org/api/rest_v1"
RESEARCH_ENABLED: bool = _get_bool("NARRA_RESEARCH_ENABLED", default=True)
RESEARCH_TIMEOUT_SECONDS: float = float(os.getenv("RESEARCH_TIMEOUT_SECONDS", "10"))

# --- Local fallback models (only imported/loaded if Gemini is unavailable) ---
LOCAL_FALLBACK_ENABLED: bool = _get_bool("NARRA_LOCAL_FALLBACK", default=True)
NARRA_USE_CUDA: str = os.getenv("NARRA_USE_CUDA", "auto")

# --- CORS ---
FRONTEND_ORIGINS = [
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
