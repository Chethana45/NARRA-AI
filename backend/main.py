import logging
import traceback
from io import BytesIO
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import config
from services import story_pipeline
from services.tts import TextToSpeechService
from utils.image_utils import load_and_resize_image, validate_image_bytes

BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "generated_audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="NARRA.AI API",
    description="AI backend for image storytelling, captioning, and narration.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.FRONTEND_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.mount("/generated_audio", StaticFiles(directory=AUDIO_DIR), name="generated_audio")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("narra.backend")

tts_service = TextToSpeechService(output_dir=AUDIO_DIR)

MAX_CONTEXT_LENGTH = 200


@app.get("/health")
def health() -> Any:
    return {
        "status": "ok",
        "message": "NARRA.AI backend is ready.",
        "mode": "gemini" if config.GEMINI_ENABLED else "local",
        "research_enabled": config.RESEARCH_ENABLED,
    }


@app.get("/styles")
def styles() -> Any:
    return {"styles": sorted({story_pipeline.normalize_style(s) for s in story_pipeline.STYLE_OPTIONS})}


@app.post("/generate")
async def generate(
    image: UploadFile = File(...),
    style: str = Form(...),
    context: str = Form(""),
) -> Any:
    content = await image.read()
    try:
        validate_image_bytes(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a supported image.")

    if style not in story_pipeline.STYLE_OPTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid style. Choose from: {', '.join(sorted(story_pipeline.STYLE_OPTIONS))}.",
        )

    user_context = (context or "").strip()[:MAX_CONTEXT_LENGTH]

    try:
        processed_image = load_and_resize_image(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Re-encode the resized image to bytes for the vision stage (keeps upload
    # size in check while still giving Gemini/BLIP a clean, valid image).
    buf = BytesIO()
    processed_image.save(buf, format="JPEG", quality=92)
    processed_bytes = buf.getvalue()

    try:
        logger.info("Running NARRA pipeline (context=%r, style=%r)", user_context, style)
        result = story_pipeline.run_pipeline(
            image_bytes=processed_bytes,
            mime_type="image/jpeg",
            style=style,
            user_context=user_context,
        )
    except Exception as exc:
        logger.exception("Pipeline failed: %s", exc)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to analyze image and generate story: {exc}")

    warnings = list(result.warnings)

    audio_url = None
    try:
        logger.info("Starting TTS synthesis")
        audio_path = tts_service.synthesize(result.story)
        if audio_path:
            audio_url = f"/generated_audio/{Path(audio_path).name}"
            logger.info("Audio generated: %s", audio_url)
        else:
            logger.warning("TTS synthesis returned no audio path")
            warnings.append("Audio generation failed (narration text and story are still available).")
    except Exception:
        logger.exception("TTS synthesis failed")
        traceback.print_exc()
        warnings.append("Audio generation failed (narration text and story are still available).")

    response_payload = {
        "caption": result.caption,
        "story": result.story,
        "audio_url": audio_url,
        "mode": result.mode,
        "visual_analysis": result.visual_analysis,
        "research": result.research,
    }
    if warnings:
        response_payload["warning"] = " ".join(warnings)
    return JSONResponse(content=response_payload)
