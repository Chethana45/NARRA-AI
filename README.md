# NARRA.AI

NARRA.AI turns an uploaded image into a grounded, tone-aware story with AI narration.
It understands the image, optionally researches real facts about a person/place/event
you name, and clearly separates what it *observed*, what it *inferred*, and what
*verified facts* (with source) it used — instead of generating a random caption.

## Architecture

```
IMAGE
  -> VISION ANALYSIS            (Gemini vision, or local BLIP+OCR fallback)
  -> STRUCTURED VISUAL DESCRIPTION   (observed / inferred / unknown)
  -> USER CONTEXT (optional name/place/event)
  -> KNOWLEDGE RESEARCH          (Wikipedia, no API key needed)
  -> FACT VERIFICATION           (only Wikipedia-sourced sentences count as "verified")
  -> STORY PLANNING              (structured prompt merges visuals + facts + tone)
  -> CAPTION + STORY GENERATION  (Gemini, or local FLAN-T5 fallback)
  -> TEXT-TO-SPEECH              (pyttsx3, offline)
  -> FINAL RESULT
```

- `frontend/`: React + Vite + Tailwind app (unchanged visual design, extended with
  a "Who/what is this about?" field, more tone options, and a transparency panel
  showing observed/inferred details and research sources).
- `backend/main.py`: FastAPI app, single `/generate` endpoint plus `/health` and `/styles`.
- `backend/config.py`: loads `GEMINI_API_KEY` and other settings from `backend/.env`
  (never hard-coded, never committed).
- `backend/services/gemini_client.py`: Gemini REST wrapper for vision + text, using
  structured JSON schemas so the model can't go off-script.
- `backend/services/research.py`: Wikipedia search + summary lookup (no API key).
- `backend/services/story_pipeline.py`: the orchestrator described above, with
  automatic fallback to fully-local open-source models if Gemini is unavailable.
- `backend/models/local_caption.py` / `local_text_generation.py`: the original
  BLIP + FLAN-T5 models, kept as an offline fallback (heavy deps imported lazily).
- `backend/utils/ocr.py`: pytesseract-based OCR, used to enrich the local fallback.
- `backend/tests/`: automated test suite (20 tests) covering research, the Gemini
  client, pipeline fact-grounding logic, and the full `/generate` endpoint.

## Two operating modes

| | **Gemini mode** (recommended) | **Local fallback** |
|---|---|---|
| Requires | `GEMINI_API_KEY` in `backend/.env` | nothing extra |
| Vision | Full structured analysis: objects, people (generic, non-identifying), animals, places, buildings, vehicles, clothing, activities, environment, visible text, signs, mood, composition | One short BLIP caption + OCR text |
| Story quality | High, tone-aware, grounded in research facts | Basic, heuristic-based |
| Cost | Uses your Google AI Studio quota/billing | Free |

The backend automatically uses Gemini mode if a key is configured, and transparently
falls back to local mode (per-request) if Gemini errors out.

## Installation

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # or .\.venv\Scripts\Activate.ps1 on Windows

pip install -r requirements.txt
# Optional, only if you want the fully offline local fallback to work:
pip install -r requirements-local.txt
```

Copy `.env.example` to `.env` and add your key:

```bash
cp .env.example .env
# then edit .env and set:
# GEMINI_API_KEY=your-key-from-https://aistudio.google.com/app/apikey
```

`.env` is gitignored — it is never committed and never sent anywhere except to
Google's Gemini API from your own machine.

OCR also requires the system `tesseract-ocr` binary (already present on most
Linux distros; `sudo apt-get install tesseract-ocr` on Debian/Ubuntu, `brew
install tesseract` on macOS).

### Frontend

```bash
cd frontend
npm install
```

## Running locally

```bash
# Terminal 1
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2
cd frontend
npm run dev
```

Open the frontend at `http://localhost:5173` (or `http://localhost:4173` for a
production preview via `npm run build && npm run preview`).

## Endpoints

- `GET /health` — status + which mode (`gemini`/`local`) is active
- `GET /styles` — list of supported tones
- `POST /generate` — form fields: `image` (file), `style`, `context` (optional
  name/place/event). Returns `caption`, `story`, `audio_url`, `mode`,
  `visual_analysis`, `research`, and an optional `warning`.

## Hallucination control

- The vision stage is explicitly instructed never to guess a real person's
  identity from their face — only the user-provided `context` field is used
  as an identity/search hint.
- Story generation may only state factual claims (names, dates, awards,
  events) that appear in the `research.verified_facts` list. If no Wikipedia
  article is found, the prompt explicitly tells the model not to invent any
  biography and the frontend shows "No verified information found."
- Every response separates `observed` (clearly visible), `inferred`
  (reasonable guess), and `unknown` (not determinable).

## Testing

```bash
cd backend
python -m pytest tests/ -v
```

20 tests cover: Wikipedia research (found/not-found/disambiguation), the
Gemini client (structured JSON parsing, auth errors, malformed responses),
pipeline fact-grounding prompts, Gemini→local fallback behavior, and a full
mocked `/generate` request/response cycle.

Manual smoke test (`backend/test_generate.py`) exercises the real, un-mocked
pipeline end-to-end — requires a working `GEMINI_API_KEY` and/or local
model dependencies plus network access.

## Notes / known limitations

- Images are resized/re-encoded before inference. Supports JPG, JPEG, PNG,
  WEBP up to 8 MB.
- Wikipedia is the only research source; it will not have information about
  private individuals, very recent events, or niche topics — the app reports
  this honestly rather than guessing.
- pyttsx3 narration quality depends on the voices installed on your OS.
