import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
from services import gemini_client


def _mock_gemini_response(payload_dict, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.ok = status_code < 400
    resp.text = json.dumps(payload_dict)
    resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": json.dumps(payload_dict)}]}}]
    }
    return resp


def test_analyze_image_without_key_raises():
    with patch.object(config, "GEMINI_ENABLED", False):
        try:
            gemini_client.analyze_image(b"fake", "image/jpeg", None)
            assert False, "expected GeminiError"
        except gemini_client.GeminiError:
            pass


def test_generate_story_parses_structured_json():
    fake = {"caption": "A quiet morning by the sea.", "story": "Waves rolled in slowly..."}
    with patch.object(config, "GEMINI_ENABLED", True), \
         patch.object(config, "GEMINI_API_KEY", "fake-key"), \
         patch("services.gemini_client.requests.post", return_value=_mock_gemini_response(fake)):
        result = gemini_client.generate_story("some prompt")
    assert result["caption"] == fake["caption"]
    assert result["story"] == fake["story"]


def test_generate_story_bad_json_raises():
    resp = MagicMock()
    resp.status_code = 200
    resp.ok = True
    resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "not json"}]}}]
    }
    with patch.object(config, "GEMINI_ENABLED", True), \
         patch.object(config, "GEMINI_API_KEY", "fake-key"), \
         patch("services.gemini_client.requests.post", return_value=resp):
        try:
            gemini_client.generate_story("some prompt")
            assert False, "expected GeminiError"
        except gemini_client.GeminiError:
            pass


def test_unauthorized_raises_clear_error():
    resp = MagicMock()
    resp.status_code = 401
    resp.ok = False
    resp.text = "unauthorized"
    with patch.object(config, "GEMINI_ENABLED", True), \
         patch.object(config, "GEMINI_API_KEY", "bad-key"), \
         patch("services.gemini_client.requests.post", return_value=resp):
        try:
            gemini_client.generate_story("some prompt")
            assert False, "expected GeminiError"
        except gemini_client.GeminiError as exc:
            assert "key" in str(exc).lower()
