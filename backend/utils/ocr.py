"""
Local OCR helper (pytesseract + system tesseract-ocr binary).

Used mainly to enrich the LOCAL fallback pipeline (when no Gemini key is
configured) with real, observed visible text -- Gemini's vision model already
reads on-image text natively, so this is skipped in Gemini mode.
"""
from __future__ import annotations

import logging

from PIL import Image

logger = logging.getLogger("narra.ocr")

try:
    import pytesseract
    _TESSERACT_IMPORT_ERROR: Exception | None = None
except Exception as exc:  # pragma: no cover - environment dependent
    pytesseract = None  # type: ignore
    _TESSERACT_IMPORT_ERROR = exc


def is_available() -> bool:
    if pytesseract is None:
        return False
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def extract_text(image: Image.Image) -> list[str]:
    """
    Run OCR on the image and return a list of non-trivial detected text lines.
    Returns an empty list (never raises) if OCR is unavailable or finds nothing.
    """
    if not is_available():
        if _TESSERACT_IMPORT_ERROR:
            logger.info("OCR unavailable (pytesseract import failed): %s", _TESSERACT_IMPORT_ERROR)
        else:
            logger.info("OCR unavailable (tesseract-ocr binary not found on PATH).")
        return []

    try:
        raw = pytesseract.image_to_string(image.convert("RGB"))
    except Exception as exc:
        logger.warning("OCR extraction failed: %s", exc)
        return []

    lines = []
    for line in raw.splitlines():
        cleaned = line.strip()
        # Filter out empty lines and pure-noise single/double character junk
        # that OCR sometimes hallucinates from textures/backgrounds.
        if len(cleaned) >= 3 and any(c.isalnum() for c in cleaned):
            lines.append(cleaned)
    return lines
