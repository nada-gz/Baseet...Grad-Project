# Egyptian Arabic Kids Explainer — Self-Contained Pipeline

A fully self-contained video generation pipeline for Egyptian Arabic educational content for children.

## What it does

1. **Groq AI** — generates a kid-friendly Egyptian Arabic scene script from your input text
2. **NileTTS** — generates Egyptian Arabic speech for each scene (free HuggingFace Space, no API key)
3. **Pixabay Video** — downloads royalty-free background video clips per scene
4. **Pixabay Music** — downloads a royalty-free background music track (no API key)
5. **FFmpeg** — mixes narration + music (ducked so speech stays clear)
6. **Remotion** — renders an animated background video with Arabic text overlays
7. **FFmpeg** — muxes the mixed audio into the final MP4

## Folder structure

```
video/
├── run_pipeline.py          ← the only script you run
├── .env                     ← your API keys (Groq + Pixabay only)
├── requirements.txt         ← Python deps (3 packages)
├── remotion-composer/       ← Remotion renderer (Node.js)
└── projects/
    └── kids-explainer/
        ├── assets/
        │   ├── audio/       ← per-scene WAV + narration_full.wav + mixed_final.wav
        │   ├── video/       ← per-scene Pixabay clips
        │   └── music/       ← background.mp3
        ├── artifacts/       ← edit_decisions.json
        └── renders/
            ├── remotion_bg.mp4   ← silent Remotion background
            └── final.mp4         ← ✅ your finished video
```

## Setup (one time)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Remotion packages are already installed (node_modules is pre-built)
#    If they're missing, run:
cd remotion-composer && npm install && cd ..

# 3. Fill in .env (Groq key + Pixabay key — see .env file for links)
```

## Run

```bash
# Use built-in demo text (Arabic plants topic)
python run_pipeline.py

# Use your own Arabic text file
python run_pipeline.py --file topic.txt
```

The pipeline is **resumable** — if it crashes or you re-run it, already-generated files are skipped automatically.

## Requirements

| Tool | Purpose | Cost |
|------|---------|------|
| Python 3.10+ | Runtime | free |
| FFmpeg | Audio/video processing | free |
| Node.js 18+ | Remotion renderer | free |
| Groq API | LLM script generation | free tier |
| Pixabay API | Background video clips | free key |
| NileTTS HF Space | Egyptian Arabic TTS | free |
| Pixabay Music | Background music | free (no key) |
