# 🎨 NARRA.AI

<p align="center">
  <img src="https://img.shields.io/badge/AI-Powered-8B5CF6?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Computer%20Vision-Gemini-4285F4?style=for-the-badge" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" />
</p>

<p align="center">
  <b>See the image. Understand the context. Discover the story. Hear it come alive.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/Chethana45/NARRA-AI?style=flat-square" />
  <img src="https://img.shields.io/github/forks/Chethana45/NARRA-AI?style=flat-square" />
  <img src="https://img.shields.io/github/last-commit/Chethana45/NARRA-AI?style=flat-square" />
</p>

---

## ✨ What is NARRA.AI?

**NARRA.AI** transforms an uploaded image into a **grounded, tone-aware story with AI narration**.

Instead of simply generating a random caption, NARRA.AI goes through multiple stages to understand the image, optionally research a person, place, or event provided by the user, and clearly distinguish between:

> 👁️ **What it observed**  
> 💭 **What it inferred**  
> 📚 **What it verified**

The final result combines visual understanding, factual research, story generation, and text-to-speech into one pipeline.

---

# 🌈 Core Idea

```text
             📷 IMAGE
                │
                ▼
       👁️ VISION ANALYSIS
                │
                ▼
    📝 STRUCTURED DESCRIPTION
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
    👁️ OBSERVED       💭 INFERRED
        │                │
        └───────┬────────┘
                │
                ▼
       👤 USER CONTEXT
                │
                ▼
       🔎 KNOWLEDGE RESEARCH
                │
                ▼
        ✅ FACT VERIFICATION
                │
                ▼
        📖 STORY PLANNING
                │
                ▼
       ✨ STORY GENERATION
                │
                ▼
          🔊 AI NARRATION
                │
                ▼
          🎬 FINAL RESULT
```

---

# 🚀 What Makes It Different?

Most image-to-text applications simply produce a caption.

NARRA.AI focuses on **grounded storytelling**.

| Traditional Image Captioning | NARRA.AI |
|---|---|
| 📝 Generates a caption | 📖 Generates a complete story |
| 👁️ Describes the image | 👁️ Separates observations and inferences |
| ❓ May guess facts | ✅ Uses verified research for factual claims |
| 🎭 Limited tone control | 🎨 Tone-aware storytelling |
| 🔊 Usually text only | 🔊 Includes narration |
| 📚 No external context | 🔎 Optional Wikipedia research |
| 🧠 Black-box output | 🔍 Transparency panel |

---

# 🏗️ Architecture

```text
┌──────────────────────┐
│       📷 IMAGE       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   👁️ Vision Analysis │
│   Gemini / BLIP      │
│   + OCR              │
└──────────┬───────────┘
           │
           ▼
┌────────────────────────────┐
│ 📝 Structured Visual       │
│    Description             │
│                            │
│ • Observed                 │
│ • Inferred                 │
│ • Unknown                  │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ 👤 Optional User Context   │
│                            │
│ Person / Place / Event     │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ 🔎 Knowledge Research      │
│                            │
│ Wikipedia                  │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ ✅ Fact Verification       │
│                            │
│ Verified Facts Only        │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ 📖 Story Planning          │
│                            │
│ Visuals + Facts + Tone     │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ ✨ Story Generation        │
│                            │
│ Gemini / FLAN-T5           │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ 🔊 Text-to-Speech          │
│                            │
│ pyttsx3                    │
└──────────┬─────────────────┘
           │
           ▼
      🎬 FINAL STORY
```

---

# 🧩 Project Structure

```text
NARRA-AI/
│
├── frontend/
│   ├── React + Vite
│   ├── Tailwind CSS
│   └── UI components
│
├── backend/
│   ├── main.py
│   ├── config.py
│   │
│   ├── services/
│   │   ├── gemini_client.py
│   │   ├── research.py
│   │   └── story_pipeline.py
│   │
│   ├── models/
│   │   ├── local_caption.py
│   │   └── local_text_generation.py
│   │
│   ├── utils/
│   │   └── ocr.py
│   │
│   ├── tests/
│   │   └── automated tests
│   │
│   ├── requirements.txt
│   └── requirements-local.txt
│
├── .env.example
├── .gitignore
└── README.md
```

---

# 🤖 AI Pipeline

## 👁️ 1. Vision Analysis

NARRA.AI analyzes the uploaded image using:

### Gemini Mode

Gemini vision performs structured analysis covering:

- Objects
- Generic people descriptions
- Animals
- Places
- Buildings
- Vehicles
- Clothing
- Activities
- Environment
- Visible text
- Signs
- Mood
- Composition

### Local Fallback

When Gemini is unavailable, the system can fall back to:

- BLIP
- OCR using Tesseract

---

# 📝 2. Structured Visual Description

The vision stage doesn't simply return a paragraph.

The result is separated into:

### 👁️ Observed

Things that are clearly visible in the image.

### 💭 Inferred

Reasonable interpretations based on visible information.

### ❓ Unknown

Information that cannot be determined from the image.

This separation helps prevent the system from presenting guesses as facts.

---

# 👤 3. User Context

The user can optionally provide context about the image.

Examples:

```text
Who or what is this about?

A historical place
A person
An event
A location
```

The provided context can then be used as a research hint.

---

# 🔎 4. Knowledge Research

NARRA.AI uses **Wikipedia** for optional knowledge research.

The research stage can:

- Search for the provided context
- Retrieve relevant summaries
- Extract factual information
- Provide sources for verified information

No Wikipedia API key is required.

---

# ✅ 5. Fact Verification

A major feature of NARRA.AI is its approach to factual claims.

Only information present in the:

```text
research.verified_facts
```

list can be treated as verified factual information during story generation.

If no relevant Wikipedia article is found, the system does **not** invent a biography.

Instead, the application reports:

> **No verified information found.**

---

# 📖 6. Story Generation

The story generation stage combines:

```text
Visual Analysis
      +
User Context
      +
Verified Facts
      +
Selected Tone
      ↓
Story Planning
      ↓
Final Story
```

This allows the generated story to remain connected to what the system actually knows about the image.

---

# 🎭 Tone-Aware Stories

NARRA.AI supports different storytelling tones through the frontend.

The selected tone becomes part of the story-generation process.

This allows the same image to be transformed into different storytelling styles while keeping the visual and factual grounding.

---

# 🔊 7. AI Narration

Generated stories can be converted into audio using:

**pyttsx3**

The narration works offline and depends on the voices available on the user's operating system.

---

# 🔄 Two Operating Modes

NARRA.AI supports two operating modes.

| Feature | 🟣 Gemini Mode | 🟢 Local Fallback |
|---|---|---|
| API Key | `GEMINI_API_KEY` | Not required |
| Vision | Gemini Vision | BLIP |
| OCR | Available | Tesseract |
| Story Generation | Gemini | FLAN-T5 |
| Research | Wikipedia | Wikipedia |
| Narration | pyttsx3 | pyttsx3 |
| Internet | Required for Gemini/research | Local inference available |
| Cost | Uses Google AI Studio quota/billing | Free |

### Automatic Fallback

If Gemini is configured but an error occurs, the backend can automatically fall back to the local pipeline for that request.

```text
Gemini Available?
      │
   ┌──┴──┐
  YES    NO
   │      │
   ▼      ▼
Gemini   Local
   │      │
   └──┬───┘
      ▼
 Final Story
```

---

# 🛡️ Hallucination Control

NARRA.AI is designed with explicit grounding rules.

### 🔐 Identity Protection

The vision stage is instructed **not to guess the identity of a real person from their face**.

Only the user-provided context is used as an identity or research hint.

### 📚 Verified Facts

Factual claims about:

- Names
- Dates
- Awards
- Events
- Biographical information

must come from the verified research information.

### 🔍 Transparency

Every response separates information into:

```text
👁️ OBSERVED
💭 INFERRED
❓ UNKNOWN
✅ VERIFIED FACTS
```

This makes it easier to understand where different pieces of information came from.

---

# 🖥️ Frontend

The frontend is built using:

- ⚛️ React
- ⚡ Vite
- 🎨 Tailwind CSS

The interface includes:

- Image upload
- Context input
- Tone selection
- Generated caption
- Generated story
- Audio narration
- Visual analysis
- Research information
- Source transparency

---

# ⚙️ Backend

The backend is built using:

- 🐍 Python
- ⚡ FastAPI
- 🤖 Gemini
- 🧠 BLIP
- ✍️ FLAN-T5
- 🔎 Wikipedia
- 🔤 Tesseract OCR
- 🔊 pyttsx3

The backend exposes a small API centered around the story-generation pipeline.

---

# 🔌 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Check backend status and active mode |
| `GET` | `/styles` | Get supported storytelling tones |
| `POST` | `/generate` | Generate caption, story and narration |

### `/generate`

Accepts:

```text
image
style
context (optional)
```

Returns:

```text
caption
story
audio_url
mode
visual_analysis
research
warning (optional)
```

---

# 🧪 Testing

NARRA.AI includes an automated test suite.

Run:

```bash
cd backend
python -m pytest tests/ -v
```

The test suite contains **20 tests** covering:

- Wikipedia research
- Research not-found cases
- Research disambiguation
- Gemini client
- Structured JSON parsing
- Authentication errors
- Malformed responses
- Fact-grounding logic
- Gemini → local fallback
- `/generate` endpoint

---

# 🔬 Manual Smoke Test

A manual end-to-end test is also available:

```bash
cd backend
python test_generate.py
```

This exercises the real, unmocked pipeline.

A working:

```text
GEMINI_API_KEY
```

and/or local model dependencies may be required.

Network access may also be required.

---

# 🛠️ Installation

## Backend

```bash
cd backend

python -m venv .venv
```

### Windows

```powershell
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install the main dependencies:

```bash
pip install -r requirements.txt
```

For the fully offline local fallback:

```bash
pip install -r requirements-local.txt
```

---

# 🔑 Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Then add:

```env
GEMINI_API_KEY=your-api-key
```

The API key should remain inside:

```text
backend/.env
```

and should **never be committed to GitHub**.

---

# 🔤 OCR Requirement

OCR uses the **Tesseract** system binary.

### Ubuntu / Debian

```bash
sudo apt-get install tesseract-ocr
```

### macOS

```bash
brew install tesseract
```

---

# 🌐 Frontend Installation

```bash
cd frontend
npm install
```

---

# ▶️ Running Locally

### Terminal 1 — Backend

```bash
cd backend

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2 — Frontend

```bash
cd frontend

npm run dev
```

Open:

```text
http://localhost:5173
```

For a production preview:

```bash
npm run build
npm run preview
```

The preview is available at:

```text
http://localhost:4173
```

---

# 📋 Example Workflow

```text
1. Upload an image
        ↓
2. Select a storytelling tone
        ↓
3. Optionally enter a person/place/event
        ↓
4. NARRA.AI analyzes the image
        ↓
5. Visual details are separated
        ↓
6. Wikipedia research is performed
        ↓
7. Verified facts are extracted
        ↓
8. Story is planned
        ↓
9. Caption + story are generated
        ↓
10. Story is converted to narration
        ↓
11. Final result is displayed
```

---

# 📌 Known Limitations

- Images are resized/re-encoded before inference.
- Supported image formats include JPG, JPEG, PNG and WEBP.
- Maximum image size is **8 MB**.
- Wikipedia is currently the only research source.
- Wikipedia may not contain information about private individuals.
- Very recent events may not be available.
- Niche topics may not have useful Wikipedia coverage.
- pyttsx3 narration quality depends on voices installed on the operating system.
- Local fallback models require additional dependencies and can be computationally heavy.

---

# 🧰 Tech Stack

| Category | Technology |
|---|---|
| Frontend | React |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| Backend | FastAPI |
| Language | Python |
| Vision | Gemini Vision / BLIP |
| Text Generation | Gemini / FLAN-T5 |
| OCR | Tesseract / pytesseract |
| Research | Wikipedia |
| Text-to-Speech | pyttsx3 |
| Testing | Pytest |
| Version Control | Git / GitHub |

---

# 🌟 Key Features

### 📷 Image Understanding
Analyze uploaded images using AI vision models.

### 📖 Grounded Storytelling
Generate stories based on visual information and verified context.

### 🔎 Knowledge Research
Research user-provided people, places, and events through Wikipedia.

### 🛡️ Hallucination Control
Separate observations, inferences, unknown information, and verified facts.

### 🎭 Tone-Aware Generation
Generate stories according to the selected storytelling style.

### 🔊 AI Narration
Convert generated stories into audio using pyttsx3.

### 🔄 Automatic Fallback
Switch between Gemini and local models when required.

### 🧪 Automated Testing
20 automated tests cover important backend functionality.

---

# 🚀 Future Scope

Potential improvements include:

- 🌐 Additional research sources
- 🎙️ More natural TTS voices
- 🌍 Multilingual storytelling
- 🎨 More storytelling styles
- 📚 Additional knowledge sources
- 🧠 More local AI models
- 📱 Improved mobile experience
- 🔊 Advanced narration controls
- 📊 More detailed visual analytics

---

# ⚠️ Important

NARRA.AI is designed as an **AI-powered storytelling and image-understanding application**.

Its generated content should be treated as AI-generated output. Visual inferences are not guaranteed facts, and verified information depends on the availability and accuracy of the research source.

---

# 👩‍💻 Author

## Chethana Sri

**B.E. Computer Science Engineering**  
**Madras Institute of Technology**

---

<p align="center">

### 🎨 NARRA.AI

<b>Turn Images Into Stories.  
Ground Them In Reality.  
Bring Them To Life. 🎙️</b>

</p>

<p align="center">
  <img src="https://img.shields.io/badge/Built%20with-React%20%2B%20FastAPI-8B5CF6?style=for-the-badge" />
</p>
