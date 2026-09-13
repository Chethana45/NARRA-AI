import re
import uuid
from pathlib import Path
from typing import Optional

import pyttsx3


def _prepare_narration_text(text: str) -> str:
    """
    Light cleanup so narration paces naturally: collapse whitespace, ensure
    sentences end with clear terminal punctuation (helps pyttsx3 insert
    pauses at sentence boundaries), and drop stray markdown/JSON artifacts
    the upstream model might leave behind.
    """
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = re.sub(r"[*_`#]+", "", cleaned)  # strip stray markdown
    cleaned = re.sub(r"\s+", " ", cleaned)
    # Ensure a pause (period) exists between sentences that got glued together.
    cleaned = re.sub(r"([.!?])([A-Z])", r"\1 \2", cleaned)
    return cleaned.strip()


class TextToSpeechService:
    def __init__(self, output_dir: str) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, text: str) -> Optional[str]:
        narration_text = _prepare_narration_text(text)
        if not narration_text:
            return None
        try:
            file_name = f"narration_{uuid.uuid4().hex}.wav"
            output_path = self.output_dir / file_name
            engine = pyttsx3.init()
            engine.setProperty("rate", 168)
            engine.setProperty("volume", 1.0)
            voices = engine.getProperty("voices")
            if voices:
                engine.setProperty("voice", voices[0].id)
            engine.save_to_file(narration_text, str(output_path))
            engine.runAndWait()
            if not output_path.exists() or output_path.stat().st_size == 0:
                return None
            return str(output_path)
        except Exception:
            return None
