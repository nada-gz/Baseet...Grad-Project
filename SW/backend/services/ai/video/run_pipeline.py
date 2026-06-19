"""
Egyptian Arabic Kids Explainer Pipeline
========================================
Self-contained. No external tool framework.

Steps:
  1. Groq AI  → generate scene script (JSON)
  2. NileTTS  → per-scene Egyptian-Arabic WAV files
  3. Concat   → stitch WAV files into one full_audio.wav
  4. Pixabay  → download per-scene background video clips
  5. Music    → download royalty-free background music (Pixabay)
  6. Mix      → ducked mix of narration + music via FFmpeg
  7. Remotion → render silent animated background video
  8. Mux      → combine Remotion video + mixed audio → final MP4

Usage:
  python run_pipeline.py                    # uses built-in demo text
  python run_pipeline.py --file topic.txt   # reads Arabic text from file
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# ── Force UTF-8 on Windows ──────────────────────────────────────────────────
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()
backend_env = Path(__file__).parent.parent.parent.parent / ".env"
if backend_env.exists():
    load_dotenv(dotenv_path=backend_env)

PROJECT_ROOT = Path(__file__).parent
REMOTION_DIR = PROJECT_ROOT / "remotion-composer"

# Dynamic initialization helper
PROJECT_DIR = PROJECT_ROOT / "projects" / "kids-explainer"
TEMP_ASSETS = PROJECT_DIR / "temp_remotion_assets"

def init_project_dirs(session_id: str):
    global PROJECT_DIR, TEMP_ASSETS
    PROJECT_DIR = PROJECT_ROOT / "projects" / session_id
    for sub in ["artifacts", "assets/video", "assets/audio", "assets/music", "renders"]:
        (PROJECT_DIR / sub).mkdir(parents=True, exist_ok=True)
    TEMP_ASSETS = PROJECT_DIR / "temp_remotion_assets"
    TEMP_ASSETS.mkdir(parents=True, exist_ok=True)


def log(stage: str, msg: str) -> None:
    print(f"[{stage}] {msg}", flush=True)


# ── Theme ───────────────────────────────────────────────────────────────────
THEME_CONFIG = {
    "primaryColor": "#2D9E4F",
    "accentColor": "#F6C026",
    "backgroundColor": "#0D2416",
    "surfaceColor": "#1A3D25",
    "textColor": "#E8F5E9",
    "mutedTextColor": "#A5D6A7",
    "headingFont": "Inter",
    "bodyFont": "Inter",
    "monoFont": "JetBrains Mono",
    "chartColors": ["#2D9E4F", "#F6C026", "#81C784", "#FFA726", "#4DB6AC", "#E57373"],
    "springConfig": {"damping": 18, "stiffness": 100, "mass": 1},
    "transitionDuration": 0.4,
    "captionHighlightColor": "#F6C026",
    "captionBackgroundColor": "rgba(13, 36, 22, 0.80)",
}


# ═══════════════════════════════════════════════════════════════════════════
# STEP 1 — Generate script via Groq AI
# ═══════════════════════════════════════════════════════════════════════════
def step1_generate_script(lecture_text: str) -> list[dict]:
    import requests as req_lib

    system_prompt = """
You are an expert video director for an Egyptian children's educational channel.
You receive a lecture text and must produce a fun, engaging, and simple video script.

CRITICAL RULES:
1. Cover EVERY concept from the lecture — do not skip anything.
2. The total video MUST exceed 60 seconds. Generate at least 10–15 scenes and
   expand each idea with a story, interactive question, or fun analogy for kids.
3. Use the "callout" scene type heavily with character emojis (e.g. 👩‍🏫 🧑‍🌾 🧒 🧑‍🔬).
4. "display_text" must be natural Egyptian Arabic (Ammiya) — it will be spoken aloud.

Reply with a single valid JSON object: {"scenes": [...]}
Each scene object MUST have:
  "id"           – e.g. "s1", "s2" …
  "label"        – short English label (e.g. "Intro", "Fact 1")
  "display_text" – Egyptian Arabic text (shown on screen AND spoken)
  "subtitle"     – English translation
  "emoji"        – one relevant emoji
  "pexels_query" – 3–4 English keywords for a background stock-video search
  "scene_type"   – one of: text_card | callout | stat_card | hero_title
"""

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set in .env. Video generation script requires GROQ_API_KEY.")
    
    log("GROQ", "Generating video script from lecture text using Groq...")
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Lecture Text:\n{lecture_text}"},
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }
    resp = req_lib.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]

    scenes = _parse_scenes_from_content(content)
    if not scenes:
        raise ValueError("Script generator returned no scenes.")
    
    log("SCRIPT", f"✓ {len(scenes)} scenes generated.")
    return scenes


def _parse_scenes_from_content(content: str) -> list[dict]:
    """
    Robustly extract a list of scenes from a (possibly malformed) LLM response.

    Tries, in order:
      1. Strip markdown fences → json.loads
      2. regex-extract the outermost {...} block → json.loads
      3. regex-extract the [...] array after "scenes": → json.loads
    """
    def strip_fences(text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    # Strategy 1 — clean fences, parse directly
    try:
        data = json.loads(strip_fences(content))
        return data.get("scenes", [])
    except (json.JSONDecodeError, AttributeError):
        pass

    # Strategy 2 — extract outermost JSON object with re
    try:
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            data = json.loads(match.group())
            return data.get("scenes", [])
    except (json.JSONDecodeError, AttributeError):
        pass

    # Strategy 3 — extract the array that follows "scenes":
    try:
        match = re.search(r'"scenes"\s*:\s*(\[[\s\S]*\])', content)
        if match:
            return json.loads(match.group(1))
    except (json.JSONDecodeError, AttributeError):
        pass

    # Strategy 4 — sanitize control characters then retry strategy 1
    try:
        sanitized = re.sub(r'[\x00-\x1f\x7f](?<!["\n\t])', ' ', strip_fences(content))
        data = json.loads(sanitized)
        return data.get("scenes", [])
    except (json.JSONDecodeError, AttributeError):
        pass

    log("SCRIPT", "WARNING: All JSON parse strategies failed. Returning empty scenes list.")
    return []




# ═══════════════════════════════════════════════════════════════════════════
# STEP 2 — Generate per-scene TTS via NileTTS (niletts-tts/niletts-api)
# ═══════════════════════════════════════════════════════════════════════════
def step2_generate_tts(scenes: list[dict]) -> tuple[list[dict], list[str]]:
    try:
        from gradio_client import Client
    except ImportError:
        raise RuntimeError("gradio_client is not installed. Run: pip install gradio_client")

    # HuggingFace Spaces go to sleep after inactivity. The first connection
    # attempt often times out while the Space wakes up. We retry up to 5 times
    # with 20-second gaps so the Space has time to start.
    log("NILETTS", "Connecting to NileTTS HuggingFace Space...")
    log("NILETTS", "  (If this is the first run today the Space needs ~60s to wake up — please wait)")

    client = None
    last_err = None
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise RuntimeError("HF_TOKEN is not set in .env. Video voice generation requires HF_TOKEN.")
    for attempt in range(5):
        try:
            client = Client("niletts-tts/niletts-api", token=hf_token, httpx_kwargs={"timeout": 120})
            break
        except Exception as exc:
            last_err = exc
            wait = 20
            log("NILETTS", f"  Attempt {attempt + 1}/5 failed ({type(exc).__name__}). "
                           f"Retrying in {wait}s...")
            time.sleep(wait)

    if client is None:
        raise RuntimeError(
            f"Could not connect to NileTTS after 5 attempts.\n"
            f"Last error: {last_err}\n"
            "Tip: visit https://huggingface.co/spaces/niletts-tts/niletts-api "
            "in your browser to manually wake the Space, then re-run the pipeline."
        )

    log("NILETTS", "✓ Connected. Generating Egyptian Arabic speech...")
    audio_paths: list[str] = []

    for s in scenes:
        out_path = PROJECT_DIR / "assets" / "audio" / f"{s['id']}.wav"
        text = s.get("display_text", "")

        if not out_path.exists():
            log("NILETTS", f"  → {s['id']} ({len(text)} chars)...")
            # Retry each prediction up to 3 times in case of a transient error
            for pred_attempt in range(3):
                try:
                    generated = client.predict(text=text, api_name="/generate_speech")
                    shutil.copy2(generated, out_path)
                    break
                except Exception as exc:
                    log("NILETTS", f"    Prediction attempt {pred_attempt + 1}/3 failed: {exc}")
                    if pred_attempt < 2:
                        time.sleep(10)
                    else:
                        raise RuntimeError(
                            f"NileTTS failed for scene {s['id']} after 3 attempts: {exc}"
                        )
            time.sleep(1)  # be polite to the free HF Space

        # Measure exact duration with ffprobe
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(out_path)],
            capture_output=True, text=True,
        )
        try:
            raw_dur = float(probe.stdout.strip())
        except ValueError:
            raw_dur = 4.0
        s["duration"] = raw_dur + 0.5   # 0.5 s padding so scene doesn't cut abruptly
        audio_paths.append(str(out_path))

    log("NILETTS", f"✓ {len(audio_paths)} audio files generated and durations measured.")
    return scenes, audio_paths


# ═══════════════════════════════════════════════════════════════════════════
# STEP 3 — Concatenate per-scene audio into one full track
# ═══════════════════════════════════════════════════════════════════════════
def step3_concat_audio(audio_paths: list[str]) -> str:
    full_audio_path = PROJECT_DIR / "assets" / "audio" / "narration_full.wav"
    if full_audio_path.exists():
        log("AUDIO", "Full narration track already exists — skipping.")
        return str(full_audio_path)

    log("AUDIO", "Concatenating per-scene audio...")
    list_file = PROJECT_DIR / "assets" / "audio" / "concat_list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for p in audio_paths:
            f.write(f"file '{Path(p).absolute()}'\n")

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_file), "-c", "copy", str(full_audio_path)],
        check=True, capture_output=True,
    )
    log("AUDIO", f"✓ Narration track: {full_audio_path}")
    return str(full_audio_path)


# ═══════════════════════════════════════════════════════════════════════════
# STEP 4 — Fetch per-scene background video clips from Pixabay
# ═══════════════════════════════════════════════════════════════════════════
_PIXABAY_VIDEO_KEY = os.environ.get("PIXABAY_API_KEY", "")

def _pixabay_video_search(query: str, min_duration: int = 4) -> dict | None:
    """Query the Pixabay Videos API. Returns the first suitable hit or None."""
    params = urllib.parse.urlencode({
        "key": _PIXABAY_VIDEO_KEY,
        "q": query,
        "video_type": "film",
        "per_page": 10,
        "safesearch": "true",
    })
    url = f"https://pixabay.com/api/videos/?{params}"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            data = json.loads(r.read().decode())
    except Exception:
        return None

    for hit in data.get("hits", []):
        dur = hit.get("duration", 0)
        if dur >= min_duration:
            # Prefer HD, fall back to smaller sizes
            vids = hit.get("videos", {})
            for quality in ("large", "medium", "small", "tiny"):
                url_ = vids.get(quality, {}).get("url", "")
                if url_:
                    return {"url": url_, "duration": dur, "user": hit.get("user", "?")}
    return None


def step4_video_clips(scenes: list[dict]) -> dict[str, str]:
    log("PIXABAY", "Fetching background video clips from Pixabay...")
    if not _PIXABAY_VIDEO_KEY:
        raise RuntimeError("PIXABAY_API_KEY is not set in .env. Pixabay search requires PIXABAY_API_KEY.")

    video_files: dict[str, str] = {}
    for s in scenes:
        out = PROJECT_DIR / "assets" / "video" / f"{s['id']}.mp4"
        if out.exists():
            video_files[s["id"]] = str(out)
            continue

        query = s.get("pexels_query", "nature")
        log("PIXABAY", f"  → {s['id']}: '{query}'")
        hit = _pixabay_video_search(query, min_duration=max(4, int(s.get("duration", 4))))
        if not hit:
            # fallback generic query
            hit = _pixabay_video_search("nature children learning", min_duration=4)

        if hit:
            try:
                req = urllib.request.Request(
                    hit["url"],
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                with urllib.request.urlopen(req, timeout=60) as r:
                    out.write_bytes(r.read())
                video_files[s["id"]] = str(out)
                log("PIXABAY", f"    ✓ {s['id']} ({hit['duration']}s by {hit['user']})")
            except Exception as e:
                log("PIXABAY", f"    ✗ Download failed for {s['id']}: {e}")
        else:
            log("PIXABAY", f"    ✗ No clip found for {s['id']}")
        time.sleep(0.2)

    return video_files


# ═══════════════════════════════════════════════════════════════════════════
# STEP 5 — Download royalty-free background music from Pixabay Music
# ═══════════════════════════════════════════════════════════════════════════
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

def step5_get_music(total_duration: float) -> str | None:
    music_path = PROJECT_DIR / "assets" / "music" / "background.mp3"
    if music_path.exists():
        log("MUSIC", "Background music already exists — skipping.")
        return str(music_path)

    log("MUSIC", "Fetching royalty-free background track (Incompetech)...")
    
    # We use a known upbeat CC-BY track from Kevin MacLeod (Incompetech)
    # since Pixabay blocks automated scraping.
    mp3_url = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Monkeys%20Spinning%20Monkeys.mp3"

    log("MUSIC", "  Downloading music track...")
    req = urllib.request.Request(mp3_url, headers={
        "User-Agent": _UA,
        "Referer": "https://incompetech.com/",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            music_path.write_bytes(r.read())
        log("MUSIC", f"✓ Music downloaded: {music_path}")
        return str(music_path)
    except Exception as e:
        log("MUSIC", f"WARNING: Music download failed: {e} — continuing without music.")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# STEP 6 — Mix narration + music (ducked) via FFmpeg
# ═══════════════════════════════════════════════════════════════════════════
def step6_mix_audio(narration_path: str, music_path: str | None, total_duration: float) -> str:
    mixed_path = PROJECT_DIR / "assets" / "audio" / "mixed_final.wav"

    if music_path is None or not Path(music_path).exists():
        log("MIX", "No music — using narration only.")
        return narration_path

    if mixed_path.exists():
        log("MIX", "Mixed audio already exists — skipping.")
        return str(mixed_path)

    log("MIX", "Mixing narration + background music (ducked)...")

    # FFmpeg filter:
    #  - Loop music to cover full video length
    #  - Lower music volume (0.12) so narration is always clear
    #  - Mix both together, output duration = narration duration
    filter_complex = (
        "[1:a]volume=0.12,atrim=0:{dur},asetpts=PTS-STARTPTS[music_adj];"
        "[0:a][music_adj]amix=inputs=2:duration=first:dropout_transition=2[premix];"
        "[premix]loudnorm=I=-16:LRA=11:TP=-1.5[out]"
    ).format(dur=int(total_duration) + 5)

    cmd = [
        "ffmpeg", "-y",
        "-i", narration_path,
        "-stream_loop", "-1", "-i", music_path,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        str(mixed_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    log("MIX", f"✓ Mixed audio: {mixed_path}")
    return str(mixed_path)


# ═══════════════════════════════════════════════════════════════════════════
# STEP 7 — Build Remotion edit_decisions + render silent background video
# ═══════════════════════════════════════════════════════════════════════════
def step7_render_remotion(scenes: list[dict], video_files: dict[str, str]) -> str:
    silent_output = PROJECT_DIR / "renders" / "remotion_bg.mp4"

    # Copy video assets to a stable path for Remotion
    temp_video: dict[str, str] = {}
    for sid, vpath in video_files.items():
        dest = TEMP_ASSETS / f"v_{sid}.mp4"
        if not dest.exists():
            shutil.copy2(vpath, dest)
        temp_video[sid] = str(dest)

    cuts = []
    current_t = 0.0
    total_duration = sum(s.get("duration", 5) for s in scenes)

    for s in scenes:
        dur = s.get("duration", 5)
        vid_path = temp_video.get(s["id"])
        cut = {
            "id": s["id"],
            "source": vid_path or "",
            "in_seconds": current_t,
            "out_seconds": current_t + dur,
            "backgroundOverlay": 0.55,
            "type": "callout",
            "text": s.get("display_text", ""),
            "title": s.get("emoji", "") + " " + s.get("subtitle", ""),
            "callout_type": "info",
            "accentColor": THEME_CONFIG["accentColor"],
        }
        if vid_path:
            cut["backgroundVideo"] = vid_path
            cut["backgroundVideoStart"] = 0
        else:
            cut["backgroundColor"] = THEME_CONFIG["surfaceColor"]
        cuts.append(cut)
        current_t += dur

    edit_decisions = {
        "render_runtime": "remotion",
        "renderer_family": "explainer-teacher",
        "cuts": cuts,
        "overlays": [],
        "themeConfig": THEME_CONFIG,
        "metadata": {
            "project": "kids-explainer",
            "pipeline": "egyptian-arabic-explainer",
            "total_duration": total_duration,
        },
    }

    # Save artifacts
    ed_path = PROJECT_DIR / "artifacts" / "edit_decisions.json"
    ed_path.write_text(json.dumps(edit_decisions, ensure_ascii=False, indent=2), encoding="utf-8")

    # Render via Remotion
    log("REMOTION", "Rendering animated background video via Remotion...")
    props_path = PROJECT_DIR / "artifacts" / "remotion_props.json"
    props_path.write_text(json.dumps(edit_decisions, ensure_ascii=False), encoding="utf-8")

    api_script = REMOTION_DIR / "remotion_render_api.mjs"
    cmd = ["node", str(api_script), str(props_path), str(silent_output)]
    r = subprocess.run(cmd, cwd=str(REMOTION_DIR), text=True)

    try:
        props_path.unlink()
    except Exception:
        pass

    if r.returncode != 0 or not silent_output.exists():
        raise RuntimeError(f"Remotion render failed (exit code {r.returncode})")

    log("REMOTION", f"✓ Background video rendered: {silent_output}")
    return str(silent_output), total_duration


# ═══════════════════════════════════════════════════════════════════════════
# STEP 8 — Mux mixed audio into Remotion video → final MP4
# ═══════════════════════════════════════════════════════════════════════════
def step8_mux(remotion_bg: str, mixed_audio: str) -> str:
    final_output = PROJECT_DIR / "renders" / "final.mp4"
    log("MUX", "Muxing audio into final video...")
    cmd = [
        "ffmpeg", "-y",
        "-i", remotion_bg,
        "-i", mixed_audio,
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(final_output),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    size_mb = final_output.stat().st_size / 1024 / 1024
    log("MUX", f"✓ Final video: {final_output} ({size_mb:.1f} MB)")
    return str(final_output)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an Egyptian Arabic kids explainer video from text."
    )
    parser.add_argument(
        "--file", type=str, default=None,
        help="Path to a .txt file with the Arabic explanation text",
    )
    parser.add_argument(
        "--session", type=str, default="kids-explainer",
        help="Unique session ID for this video run",
    )
    args = parser.parse_args()

    init_project_dirs(args.session)

    print("=" * 65)
    print("Egyptian Arabic Kids Explainer Pipeline")
    print("Groq LLM  →  NileTTS  →  Pixabay  →  Remotion  →  FFmpeg")
    print("=" * 65)

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"\nERROR: File not found: '{args.file}'")
            print("Check the filename — here are the .txt files inside the video/ folder:")
            txt_files = list(PROJECT_ROOT.glob("*.txt"))
            if txt_files:
                for tf in txt_files:
                    print(f"  {tf}")
                print(f"\nDid you mean one of the above? Run with:")
                print(f"  python run_pipeline.py --file \"{txt_files[0]}\"")
            else:
                print("  (no .txt files found in the video/ folder yet)")
                print("  Create your Arabic text file there and try again.")
            sys.exit(1)

        print(f"Reading from: {file_path}")
        with open(file_path, "r", encoding="utf-8") as fh:
            lecture_text = fh.read().strip()

        if not lecture_text:
            print(f"\nERROR: The file '{file_path.name}' is empty. Please add Arabic text to it.")
            sys.exit(1)

    else:
        print("No --file given. Using built-in demo text (Arabic plants topic).")
        lecture_text = (
            "النباتات كائنات حية تتنفس وتتغذى وتنمو. تبدأ رحلة النبات من بذرة صغيرة نزرعها في التربة. "
            "تحتاج البذرة إلى الماء وأشعة الشمس لتكبر وتصبح نبتة صغيرة. "
            "وبفضل عملية البناء الضوئي، تستخدم الأوراق الخضراء ضوء الشمس لصنع الغذاء. "
            "بمرور الوقت، تكبر النبتة وتصبح شجرة كبيرة ومفيدة تعطينا الأكسجين لنتنفس."
        )

    t0 = time.time()

    scenes                   = step1_generate_script(lecture_text)
    scenes, audio_paths      = step2_generate_tts(scenes)
    narration                = step3_concat_audio(audio_paths)
    video_files              = step4_video_clips(scenes)
    total_dur                = sum(s.get("duration", 5) for s in scenes)
    music                    = step5_get_music(total_dur)
    mixed_audio              = step6_mix_audio(narration, music, total_dur)
    remotion_bg, total_dur   = step7_render_remotion(scenes, video_files)
    final_video              = step8_mux(remotion_bg, mixed_audio)

    elapsed = time.time() - t0
    print()
    print("=" * 65)
    print(f"PIPELINE COMPLETE in {elapsed:.0f}s")
    print(f"  Output   : {final_video}")
    print(f"  Scenes   : {len(scenes)}")
    print(f"  Duration : ~{total_dur:.1f}s")
    print("=" * 65)


if __name__ == "__main__":
    main()
