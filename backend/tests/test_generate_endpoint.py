import io
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image
from fastapi.testclient import TestClient

import config
from main import app
from services import story_pipeline

client = TestClient(app)


def _image_bytes():
    img = Image.new("RGB", (256, 256), color=(20, 130, 210))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf


def test_generate_end_to_end_gemini_mode():
    vision_fixture = {
        "visual_summary": "A calm blue-toned image with soft lighting.",
        "scene_type": "abstract",
        "mood": "calm",
        "composition": "flat color, centered",
        "observed": {**story_pipeline._EMPTY_OBSERVED, "objects": ["solid color background"]},
        "inferred": [],
        "unknown": [],
    }
    story_fixture = {"caption": "Stillness in blue.", "story": "A wash of blue settles over everything, quiet and unhurried, like the pause before a memory begins."}

    with patch.object(config, "GEMINI_ENABLED", True), \
         patch("services.story_pipeline._run_vision_gemini", return_value=vision_fixture), \
         patch("services.gemini_client.generate_story", return_value=story_fixture), \
         patch("services.tts.TextToSpeechService.synthesize", return_value=None):
        resp = client.post(
            "/generate",
            files={"image": ("test.jpg", _image_bytes(), "image/jpeg")},
            data={"style": "Cinematic", "context": ""},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["caption"] == story_fixture["caption"]
    assert data["story"] == story_fixture["story"]
    assert data["mode"] == "gemini"
    assert data["visual_analysis"]["mood"] == "calm"
    assert data["research"] is None
    assert "warning" in data  # TTS was mocked to fail


def test_generate_with_context_runs_research():
    vision_fixture = {
        "visual_summary": "A person on a stage.",
        "scene_type": "concert",
        "mood": "energetic",
        "composition": "centered",
        "observed": {**story_pipeline._EMPTY_OBSERVED, "people": ["a performer"]},
        "inferred": [],
        "unknown": [],
    }
    story_fixture = {"caption": "On stage, in the moment.", "story": "Based on the visible scene, the performer commands the stage under warm lights."}
    research_fixture = {
        "found": True,
        "query": "A. R. Rahman",
        "title": "A. R. Rahman",
        "description": "Indian composer",
        "extract": "A. R. Rahman is an Indian composer and music producer.",
        "url": "https://en.wikipedia.org/wiki/A._R._Rahman",
        "source": "Wikipedia",
        "verified_facts": ["A. R. Rahman is an Indian composer and music producer."],
        "error": None,
    }

    with patch.object(config, "GEMINI_ENABLED", True), \
         patch("services.story_pipeline._run_vision_gemini", return_value=vision_fixture), \
         patch("services.gemini_client.generate_story", return_value=story_fixture), \
         patch("services.story_pipeline.research_service.research") as mock_research, \
         patch("services.tts.TextToSpeechService.synthesize", return_value="/tmp/fake.wav"):
        mock_research.return_value.to_dict.return_value = research_fixture
        resp = client.post(
            "/generate",
            files={"image": ("test.jpg", _image_bytes(), "image/jpeg")},
            data={"style": "Informative", "context": "A. R. Rahman"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["research"]["found"] is True
    assert data["research"]["title"] == "A. R. Rahman"
    assert data["audio_url"] == "/generated_audio/fake.wav"


def test_generate_rejects_invalid_style():
    resp = client.post(
        "/generate",
        files={"image": ("test.jpg", _image_bytes(), "image/jpeg")},
        data={"style": "NotAStyle", "context": ""},
    )
    assert resp.status_code == 400


def test_generate_rejects_non_image_file():
    resp = client.post(
        "/generate",
        files={"image": ("test.txt", io.BytesIO(b"hello world"), "text/plain")},
        data={"style": "Natural", "context": ""},
    )
    assert resp.status_code == 400


def test_health_and_styles_endpoints():
    r = client.get("/health")
    assert r.status_code == 200
    assert "mode" in r.json()

    r2 = client.get("/styles")
    assert r2.status_code == 200
    assert "Natural" in r2.json()["styles"]
