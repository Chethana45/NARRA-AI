import io
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image

import config
from services import gemini_client, story_pipeline


def _tiny_jpeg_bytes() -> bytes:
    img = Image.new("RGB", (64, 64), color=(10, 120, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


VISUAL_ANALYSIS_FIXTURE = {
    "visual_summary": "A person standing on a stage holding a microphone.",
    "scene_type": "concert",
    "mood": "energetic",
    "composition": "centered subject, stage lighting",
    "observed": {
        "objects": ["microphone", "stage lights"],
        "people": ["a man in a black jacket"],
        "animals": [],
        "places": [],
        "buildings": [],
        "vehicles": [],
        "clothing": ["black jacket"],
        "activities": ["performing"],
        "environment": ["stage", "concert hall"],
        "visible_text": [],
        "signs": [],
    },
    "inferred": ["likely a live music performance"],
    "unknown": [],
}


def test_style_normalization_aliases():
    assert story_pipeline.normalize_style("Storytelling") == "Cinematic"
    assert story_pipeline.normalize_style("Natural Aesthetic") == "Natural"
    assert story_pipeline.normalize_style("Funny") == "Funny"


def test_prompt_includes_verified_facts_when_found():
    research_result = {
        "found": True,
        "title": "A. R. Rahman",
        "source": "Wikipedia",
        "url": "https://en.wikipedia.org/wiki/A._R._Rahman",
        "verified_facts": ["A. R. Rahman is an Indian composer.", "He has won two Academy Awards."],
    }
    prompt = story_pipeline._build_gemini_story_prompt(VISUAL_ANALYSIS_FIXTURE, research_result, "Cinematic", "A. R. Rahman")
    assert "VERIFIED FACTS about 'A. R. Rahman'" in prompt
    assert "Academy Awards" in prompt
    assert "microphone" in prompt  # visual grounding present too


def test_prompt_explicitly_forbids_invention_when_not_found():
    research_result = {"found": False, "error": "No Wikipedia article found for 'Zzqnotarealperson'."}
    prompt = story_pipeline._build_gemini_story_prompt(VISUAL_ANALYSIS_FIXTURE, research_result, "Cinematic", "Zzqnotarealperson")
    assert "none found for 'Zzqnotarealperson'" in prompt
    assert "Do not invent" in prompt


def test_prompt_not_applicable_when_no_context():
    prompt = story_pipeline._build_gemini_story_prompt(VISUAL_ANALYSIS_FIXTURE, None, "Cinematic", "")
    assert "not applicable" in prompt


def test_vision_stage_falls_back_to_local_on_gemini_error():
    warnings = []
    img = Image.new("RGB", (32, 32))
    with patch.object(config, "GEMINI_ENABLED", True), \
         patch("services.story_pipeline._run_vision_gemini", side_effect=gemini_client.GeminiError("boom")), \
         patch("services.story_pipeline._run_vision_local", return_value=({"visual_summary": "a blue square", "observed": story_pipeline._EMPTY_OBSERVED, "inferred": [], "unknown": []}, "a blue square")):
        analysis, mode = story_pipeline.run_vision_stage(b"fake", img, "image/jpeg", "", warnings)

    assert mode == "local"
    assert any("Gemini vision analysis unavailable" in w for w in warnings)


def test_story_stage_falls_back_to_local_when_gemini_incomplete():
    warnings = []
    with patch.object(config, "GEMINI_ENABLED", True), \
         patch("services.gemini_client.generate_story", return_value={"caption": "", "story": ""}), \
         patch("models.local_text_generation.TextGenerationModel") as MockModel:
        instance = MockModel.return_value
        instance.generate_story.return_value = "A fallback story about the stage."
        caption, story = story_pipeline.run_story_stage(
            VISUAL_ANALYSIS_FIXTURE, None, "Cinematic", "", "gemini", warnings
        )

    assert story == "A fallback story about the stage."
    assert any("incomplete" in w for w in warnings)


def test_run_research_stage_returns_none_when_no_context():
    assert story_pipeline.run_research_stage("") is None
    assert story_pipeline.run_research_stage("   ") is None
