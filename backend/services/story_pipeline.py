"""
The NARRA.AI multi-stage pipeline.

    IMAGE -> VISION ANALYSIS -> STRUCTURED VISUAL DESCRIPTION -> USER CONTEXT
    -> KNOWLEDGE RESEARCH -> FACT VERIFICATION -> STORY PLANNING
    -> CAPTION + STORY GENERATION -> (caller does TTS) -> FINAL RESULT

Two interchangeable "brains" for the vision + generation stages:
  - GEMINI mode (config.GEMINI_ENABLED): Google Gemini vision+text, structured
    JSON output, grounded on real research facts. This is the primary,
    higher-quality path.
  - LOCAL mode (fallback): BLIP caption + OCR + FLAN-T5, fully offline, used
    automatically when no GEMINI_API_KEY is configured, or if Gemini fails.

Every stage produces plain, structured (JSON-serializable) data so the final
API response can show the user exactly what was OBSERVED vs INFERRED vs
UNKNOWN, and which facts were VERIFIED (with source) vs not found.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any, Optional

from PIL import Image

import config
from services import gemini_client, research as research_service
from utils import ocr

logger = logging.getLogger("narra.pipeline")

STYLE_OPTIONS = {
    "Natural", "Funny", "Cinematic", "Emotional", "Informative",
    "Inspirational", "Mysterious",
    # legacy aliases from the original app, kept working
    "Natural Aesthetic", "Professional", "Storytelling",
}

_STYLE_ALIASES = {
    "Natural Aesthetic": "Natural",
    "Professional": "Informative",
    "Storytelling": "Cinematic",
}


def normalize_style(style: str) -> str:
    return _STYLE_ALIASES.get(style, style)


@dataclass
class PipelineResult:
    mode: str  # "gemini" | "local"
    caption: str
    story: str
    visual_analysis: dict[str, Any]
    research: Optional[dict[str, Any]]
    warnings: list[str] = field(default_factory=list)


_EMPTY_OBSERVED = {
    "objects": [], "people": [], "animals": [], "places": [], "buildings": [],
    "vehicles": [], "clothing": [], "activities": [], "environment": [],
    "visible_text": [], "signs": [],
}


def _run_vision_gemini(image_bytes: bytes, mime_type: str, user_context: str) -> dict[str, Any]:
    analysis = gemini_client.analyze_image(image_bytes, mime_type, user_context or None)
    # Defensive normalization in case the model omits an optional key despite the schema.
    analysis.setdefault("observed", dict(_EMPTY_OBSERVED))
    for key, default in _EMPTY_OBSERVED.items():
        analysis["observed"].setdefault(key, default)
    analysis.setdefault("inferred", [])
    analysis.setdefault("unknown", [])
    return analysis


def _run_vision_local(image: Image.Image) -> tuple[dict[str, Any], str]:
    """Returns (structured_analysis, raw_caption) using BLIP + local OCR."""
    from models.local_caption import ImageCaptionModel  # lazy: heavy deps

    device = "cuda" if config.NARRA_USE_CUDA == "true" else "cpu"
    caption_model = ImageCaptionModel(device=device)
    caption = caption_model.generate_caption(image)

    text_lines = ocr.extract_text(image)

    analysis = {
        "visual_summary": caption,
        "scene_type": "unknown",
        "mood": "unknown",
        "composition": "unknown",
        "observed": {**_EMPTY_OBSERVED, "visible_text": text_lines},
        "inferred": [],
        "unknown": [
            "Detailed object/people/animal breakdown is not available in local "
            "fallback mode (requires a configured GEMINI_API_KEY for full "
            "structured vision analysis)."
        ],
    }
    return analysis, caption


def run_vision_stage(image_bytes: bytes, image: Image.Image, mime_type: str, user_context: str, warnings: list[str]) -> tuple[dict[str, Any], str]:
    """
    Returns (visual_analysis, mode) where mode is 'gemini' or 'local'.
    Falls back to local automatically if Gemini is unavailable or errors out.
    """
    if config.GEMINI_ENABLED:
        try:
            analysis = _run_vision_gemini(image_bytes, mime_type, user_context)
            return analysis, "gemini"
        except gemini_client.GeminiError as exc:
            logger.warning("Gemini vision analysis failed, falling back to local: %s", exc)
            warnings.append(f"Gemini vision analysis unavailable ({exc}); used local fallback instead.")

    if not config.LOCAL_FALLBACK_ENABLED:
        raise RuntimeError(
            "Gemini is unavailable and local fallback is disabled. "
            "Configure GEMINI_API_KEY in backend/.env, or set NARRA_LOCAL_FALLBACK=true."
        )

    analysis, _caption = _run_vision_local(image)
    return analysis, "local"


def run_research_stage(user_context: str) -> Optional[dict[str, Any]]:
    if not user_context or not user_context.strip():
        return None
    result = research_service.research(user_context)
    return result.to_dict()


def _build_gemini_story_prompt(visual_analysis: dict[str, Any], research_result: Optional[dict[str, Any]], style: str, user_context: str) -> str:
    observed = visual_analysis.get("observed", {})
    observed_lines = []
    for key, values in observed.items():
        if values:
            observed_lines.append(f"- {key}: {', '.join(values)}")
    observed_block = "\n".join(observed_lines) if observed_lines else "(nothing specific detected)"

    inferred_block = "\n".join(f"- {i}" for i in visual_analysis.get("inferred", [])) or "(none)"

    if research_result and research_result.get("found"):
        facts = research_result.get("verified_facts") or []
        facts_block = "\n".join(f"- {f}" for f in facts) if facts else "(article found but no extractable sentences)"
        facts_section = (
            f"VERIFIED FACTS about '{research_result.get('title')}' (source: {research_result.get('source')}, "
            f"{research_result.get('url')}):\n{facts_block}"
        )
    elif user_context:
        facts_section = (
            f"VERIFIED FACTS: none found for '{user_context}' "
            f"({research_result.get('error') if research_result else 'research not run'}). "
            "Do not invent any biographical or factual details about this name/topic."
        )
    else:
        facts_section = "VERIFIED FACTS: not applicable (no name/topic provided by the user)."

    return (
        f"VISUAL SUMMARY: {visual_analysis.get('visual_summary', '')}\n"
        f"SCENE TYPE: {visual_analysis.get('scene_type', 'unknown')}\n"
        f"MOOD: {visual_analysis.get('mood', 'unknown')}\n"
        f"COMPOSITION: {visual_analysis.get('composition', 'unknown')}\n\n"
        f"OBSERVED VISUAL DETAILS:\n{observed_block}\n\n"
        f"INFERRED (reasonable guesses, not certain):\n{inferred_block}\n\n"
        f"{facts_section}\n\n"
        f"REQUESTED TONE: {style}\n\n"
        "Write the caption and story now, following all rules in your instructions."
    )


def run_story_stage(
    visual_analysis: dict[str, Any],
    research_result: Optional[dict[str, Any]],
    style: str,
    user_context: str,
    mode: str,
    warnings: list[str],
) -> tuple[str, str]:
    """Returns (caption, story)."""
    style = normalize_style(style)

    if mode == "gemini":
        prompt = _build_gemini_story_prompt(visual_analysis, research_result, style, user_context)
        try:
            result = gemini_client.generate_story(prompt)
            caption = (result.get("caption") or "").strip()
            story = (result.get("story") or "").strip()
            if caption and story:
                return caption, story
            warnings.append("Gemini returned an incomplete story; used local fallback instead.")
        except gemini_client.GeminiError as exc:
            logger.warning("Gemini story generation failed, falling back to local: %s", exc)
            warnings.append(f"Gemini story generation unavailable ({exc}); used local fallback instead.")

    # Local fallback path (either mode=="local" from the start, or Gemini text-gen failed above)
    if not config.LOCAL_FALLBACK_ENABLED:
        raise RuntimeError("Story generation failed and local fallback is disabled.")

    from models.local_text_generation import TextGenerationModel  # lazy: heavy deps

    device = "cuda" if config.NARRA_USE_CUDA == "true" else "cpu"
    text_model = TextGenerationModel(device=device)
    caption = visual_analysis.get("visual_summary", "") or "An interesting image."
    facts = (research_result or {}).get("verified_facts") if research_result else None
    story = text_model.generate_story(caption, style, facts=facts, user_context=user_context or None)
    if not story:
        warnings.append("Local story generation could not produce a confident result.")
        story = caption
    return caption, story


def run_pipeline(image_bytes: bytes, mime_type: str, style: str, user_context: str) -> PipelineResult:
    warnings: list[str] = []

    image = Image.open(BytesIO(image_bytes))
    image = image.convert("RGB")

    visual_analysis, mode = run_vision_stage(image_bytes, image, mime_type, user_context, warnings)
    research_result = run_research_stage(user_context)
    if user_context and research_result and not research_result.get("found"):
        warnings.append(f"No verified information found for '{user_context}'. The story will not include invented facts about it.")

    caption, story = run_story_stage(visual_analysis, research_result, style, user_context, mode, warnings)

    return PipelineResult(
        mode=mode,
        caption=caption,
        story=story,
        visual_analysis=visual_analysis,
        research=research_result,
        warnings=warnings,
    )
