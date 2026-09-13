"""
Thin wrapper around the Google Gemini REST API (generateContent).

Uses plain `requests` rather than the google-generativeai SDK to keep the
dependency footprint small. Reads the API key from config (which reads it
from the environment / local .env file) -- the key is never logged, never
returned to the client, and never hard-coded.
"""
from __future__ import annotations

import base64
import json
import logging
from typing import Any, Optional

import requests

import config

logger = logging.getLogger("narra.gemini")


class GeminiError(Exception):
    """Raised when the Gemini API call fails or returns something unusable."""


# JSON schema Gemini is asked to fill in for the vision-analysis stage.
# Using an explicit responseSchema (structured output) is a key hallucination
# control: the model cannot go off and write free-form prose here, it must
# populate these exact, clearly-labeled fields.
VISION_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "visual_summary": {"type": "STRING"},
        "scene_type": {"type": "STRING"},
        "mood": {"type": "STRING"},
        "composition": {"type": "STRING"},
        "observed": {
            "type": "OBJECT",
            "properties": {
                "objects": {"type": "ARRAY", "items": {"type": "STRING"}},
                "people": {"type": "ARRAY", "items": {"type": "STRING"}},
                "animals": {"type": "ARRAY", "items": {"type": "STRING"}},
                "places": {"type": "ARRAY", "items": {"type": "STRING"}},
                "buildings": {"type": "ARRAY", "items": {"type": "STRING"}},
                "vehicles": {"type": "ARRAY", "items": {"type": "STRING"}},
                "clothing": {"type": "ARRAY", "items": {"type": "STRING"}},
                "activities": {"type": "ARRAY", "items": {"type": "STRING"}},
                "environment": {"type": "ARRAY", "items": {"type": "STRING"}},
                "visible_text": {"type": "ARRAY", "items": {"type": "STRING"}},
                "signs": {"type": "ARRAY", "items": {"type": "STRING"}},
            },
            "required": [
                "objects", "people", "animals", "places", "buildings",
                "vehicles", "clothing", "activities", "environment",
                "visible_text", "signs",
            ],
        },
        "inferred": {"type": "ARRAY", "items": {"type": "STRING"}},
        "unknown": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": [
        "visual_summary", "scene_type", "mood", "composition",
        "observed", "inferred", "unknown",
    ],
}

STORY_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "caption": {"type": "STRING"},
        "story": {"type": "STRING"},
    },
    "required": ["caption", "story"],
}

VISION_SYSTEM_INSTRUCTION = (
    "You are an image-understanding component inside a storytelling app. "
    "Describe exactly what is visible in the image, as accurately and "
    "specifically as possible. "
    "Rules you must follow strictly:\n"
    "1. Never attempt to identify a real, named individual purely from facial "
    "appearance. Describe people generically (e.g. 'a woman in a red coat'), "
    "never guess a name from their face.\n"
    "2. Separate what is clearly visible (observed) from what is a reasonable "
    "guess (inferred, e.g. 'likely a wedding based on attire and decorations') "
    "and from what cannot be determined (unknown).\n"
    "3. Transcribe any visible text/signs exactly as written; if no text is "
    "visible, return an empty list.\n"
    "4. Do not invent objects, people, or details that are not actually visible.\n"
    "5. Respond ONLY with the requested JSON structure."
)

STORY_SYSTEM_INSTRUCTION = (
    "You are a careful storytelling writer inside an app called NARRA.AI. "
    "You will be given: (a) a structured, machine-generated visual analysis of "
    "a photo, (b) optionally a short list of VERIFIED FACTS researched from "
    "reliable sources (e.g. Wikipedia) about a person/place/event the user "
    "named, and (c) a requested tone.\n\n"
    "Hard rules (hallucination control):\n"
    "1. You may only state factual claims (names, dates, awards, career "
    "events, historical facts, relationships) that literally appear in the "
    "VERIFIED FACTS section. If VERIFIED FACTS is empty or says facts were "
    "not found, do NOT invent any biography, dates, or achievements -- write "
    "about the visual scene and general, non-factual atmosphere/emotion only.\n"
    "2. Never claim to have identified who is in the photo from their face. "
    "If the user supplied a name, you may write as if the photo relates to "
    "that named context (the user asserted it), but do not claim the AI "
    "visually recognized them.\n"
    "3. Creative, imaginative language about mood, atmosphere, and feeling is "
    "encouraged and is not considered a 'fact' -- but do not dress up "
    "invented facts as if they were real.\n"
    "4. The caption must be concise (under 20 words), specific to this image, "
    "and match the requested tone. Never produce a generic caption that could "
    "apply to any photo.\n"
    "5. The story should be 90-160 words, written in the requested tone, and "
    "must be clearly grounded in the visual analysis provided.\n"
    "6. Respond ONLY with the requested JSON structure."
)


def _post(payload: dict[str, Any], model: str) -> dict[str, Any]:
    if not config.GEMINI_ENABLED:
        raise GeminiError("GEMINI_API_KEY is not configured.")

    url = f"{config.GEMINI_API_BASE}/models/{model}:generateContent"
    try:
        resp = requests.post(
            url,
            params={"key": config.GEMINI_API_KEY},
            json=payload,
            timeout=config.GEMINI_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise GeminiError(f"Network error calling Gemini: {exc}") from exc

    if resp.status_code == 401 or resp.status_code == 403:
        raise GeminiError("Gemini rejected the API key (unauthorized). Check GEMINI_API_KEY.")
    if resp.status_code == 429:
        raise GeminiError("Gemini rate limit / quota exceeded.")
    if not resp.ok:
        raise GeminiError(f"Gemini API error {resp.status_code}: {resp.text[:500]}")

    try:
        data = resp.json()
    except ValueError as exc:
        raise GeminiError("Gemini returned a non-JSON response.") from exc

    try:
        candidates = data["candidates"]
        parts = candidates[0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts)
    except (KeyError, IndexError) as exc:
        finish_reason = None
        try:
            finish_reason = data["candidates"][0].get("finishReason")
        except Exception:
            pass
        raise GeminiError(
            f"Unexpected Gemini response shape (finishReason={finish_reason})."
        ) from exc

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise GeminiError(f"Gemini did not return valid JSON: {text[:300]}") from exc


def analyze_image(image_bytes: bytes, mime_type: str, user_context: Optional[str]) -> dict[str, Any]:
    """Ask Gemini to produce a structured, grounded visual analysis of the image."""
    b64 = base64.b64encode(image_bytes).decode("ascii")

    context_note = (
        f"The user says this image relates to: \"{user_context}\". "
        "Do not use this to claim facial recognition -- just keep it in mind "
        "as context while describing what is visible."
        if user_context
        else "The user did not provide any context/name for this image."
    )

    payload = {
        "systemInstruction": {"parts": [{"text": VISION_SYSTEM_INSTRUCTION}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"inline_data": {"mime_type": mime_type, "data": b64}},
                    {"text": context_note + " Analyze the image now."},
                ],
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": VISION_RESPONSE_SCHEMA,
            "temperature": 0.2,
        },
    }
    return _post(payload, config.GEMINI_VISION_MODEL)


def generate_story(prompt_text: str) -> dict[str, Any]:
    """Ask Gemini to produce a grounded {caption, story} JSON object."""
    payload = {
        "systemInstruction": {"parts": [{"text": STORY_SYSTEM_INSTRUCTION}]},
        "contents": [{"role": "user", "parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": STORY_RESPONSE_SCHEMA,
            "temperature": 0.85,
        },
    }
    return _post(payload, config.GEMINI_TEXT_MODEL)
