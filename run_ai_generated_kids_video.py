"""
OpenMontage - AI Generated Kids Video
=============================================================
Topic: Dynamic (using dummy plants text for now)
Audience: Egyptian children 6-12
Language: Egyptian Arabic (Ammiya)
Runtime: Remotion (animated text + video composite)
Pipeline: Groq AI -> Pexels video -> Remotion render
          Audio is skipped for now to focus on video generation.
"""

import io
import json
import os
import sys
import time
import requests
import shutil
import subprocess
import tempfile
from pathlib import Path

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

PROJECT_DIR = PROJECT_ROOT / "projects" / "ai-generated-kids"
for sub in ["artifacts", "assets/video", "renders"]:
    (PROJECT_DIR / sub).mkdir(parents=True, exist_ok=True)


def log(stage, msg):
    print(f"[AI-PIPELINE][{stage}] {msg}", flush=True)


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


# ---------------------------------------------------------------------------
# STEP 1: AI Generation of Video Script via Groq
# ---------------------------------------------------------------------------
def step1_generate_script(lecture_text):
    log("THINK", "Connecting to Groq AI to generate video script...")
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not found in .env")

    # Ask the LLM to structure the response as a JSON object with a "scenes" array
    system_prompt = """
You are an expert video director for an Egyptian children's educational channel.
You receive a lecture text and must produce a fun, engaging, and simple video script.

CRITICAL RULES:
1. DO NOT SKIP ANY INFORMATION. You must cover every single concept, fact, and detail provided in the lecture text. Break it down into as many scenes as necessary.
2. VISUAL CHARACTERS: To make it engaging, you must heavily use the "callout" scene type. When using "callout", you MUST use character emojis (e.g. 👩‍🏫, 🧑‍🌾, 🧒, 🧑‍🔬) in the "emoji" field. These will animate and pop up on screen like characters explaining the video to the kids.

You must reply with a valid JSON object containing a single key "scenes" whose value is an array of scene objects.
Each scene object MUST have:
- "id": string (e.g., "s1", "s2").
- "label": Short english label (e.g., "Intro", "Fact 1").
- "display_text": Fun, simple kid-friendly Egyptian Arabic text to show on screen (max 10 words).
- "subtitle": English translation of the display_text.
- "emoji": A single relevant emoji (Use character emojis like 👩‍🏫 or 🧑‍🌾 for callouts!).
- "pexels_query": 3-4 english keywords to search for a background stock video on Pexels (e.g. "green plant growing").
- "scene_type": Prefer "callout" for explanations. Choose from ["text_card", "callout", "stat_card", "hero_title"].
- "duration": Duration in seconds (integer, usually 5 to 10).
If "scene_type" is "stat_card", also include "stat" (a number string) and "stat_subtitle" (Arabic string).
"""

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Lecture Text:\n{lecture_text}"}
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"}
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Groq API error: {response.text}")

    result_json = response.json()
    content = result_json["choices"][0]["message"]["content"]
    
    try:
        data = json.loads(content)
        scenes = data.get("scenes", [])
        if not scenes:
            raise ValueError("No scenes found in the AI response.")
        log("THINK", f"✓ AI successfully generated {len(scenes)} scenes.")
        
        # Save generated script to artifacts
        script_path = PROJECT_DIR / "artifacts" / "ai_script_v2.json"
        script_path.write_text(json.dumps(scenes, ensure_ascii=False, indent=2), encoding="utf-8")
        
        return scenes
    except Exception as e:
        log("THINK", f"Failed to parse AI output: {e}\nContent was:\n{content}")
        raise


# ---------------------------------------------------------------------------
# STEP 2: Fetch Pexels background video clips based on AI queries
# ---------------------------------------------------------------------------
def step2_video_clips(scenes):
    log("ASSETS", "Fetching Pexels video clips based on AI queries...")
    from tools.video.pexels_video import PexelsVideo
    pexels = PexelsVideo()

    video_files = {}
    for s in scenes:
        out = PROJECT_DIR / "assets" / "video" / f"{s['id']}.mp4"
        if out.exists():
            log("ASSETS", f"  {s['id']} exists, skip")
            video_files[s["id"]] = str(out)
            continue

        query = s.get("pexels_query", "nature")
        log("ASSETS", f"  Searching: '{query}'...")
        r = pexels.execute({
            "query": query,
            "orientation": "landscape",
            "size": "medium",
            "min_duration": max(4, s["duration"] - 2),
            "per_page": 5,
            "preferred_quality": "hd",
            "output_path": str(out),
        })

        if r.success:
            video_files[s["id"]] = str(out)
            log("ASSETS", f"  ✓ {s['id']}: video found by {r.data.get('user')}")
        else:
            log("ASSETS", f"  Trying fallback: 'nature'")
            r2 = pexels.execute({
                "query": "nature",
                "orientation": "landscape",
                "size": "medium",
                "per_page": 3,
                "preferred_quality": "hd",
                "output_path": str(out),
            })
            if r2.success:
                video_files[s["id"]] = str(out)
                log("ASSETS", f"  ✓ {s['id']} fallback ok")
            else:
                log("ASSETS", f"  ✗ No video for {s['id']}, will use text-only scene")

        time.sleep(0.3)

    return video_files


# ---------------------------------------------------------------------------
# STEP 3: Build Remotion edit_decisions
# ---------------------------------------------------------------------------
TEMP_ASSETS = Path("C:/Users/zeina/remotion_ai_kids_assets")

def step3_build_edit_decisions(scenes, video_files):
    log("EDIT", "Building Remotion edit_decisions...")
    TEMP_ASSETS.mkdir(parents=True, exist_ok=True)

    # Copy video files to temp dir (Remotion does not like spaces in file paths on Windows)
    temp_video = {}
    for sid, vpath in video_files.items():
        dest = TEMP_ASSETS / f"ai_v_{sid}.mp4"
        if not dest.exists():
            shutil.copy2(vpath, dest)
        temp_video[sid] = str(dest)

    cuts = []
    overlays = []
    current_t = 0.0
    total_duration = sum(s.get("duration", 5) for s in scenes)

    for s in scenes:
        dur = s.get("duration", 5)
        scene_type = s.get("scene_type", "text_card")
        vid_path = temp_video.get(s["id"])

        cut = {
            "id": s["id"],
            "source": vid_path if vid_path else "",
            "in_seconds": current_t,
            "out_seconds": current_t + dur,
            "backgroundOverlay": 0.55,
        }

        if vid_path:
            cut["backgroundVideo"] = vid_path
            cut["backgroundVideoStart"] = 0

        # Build scene type with animated Arabic text
        if scene_type == "text_card":
            cut["type"] = "text_card"
            cut["text"] = s.get("display_text", "")
            cut["fontSize"] = 90
            cut["color"] = THEME_CONFIG["textColor"]

        elif scene_type == "callout":
            cut["type"] = "callout"
            cut["text"] = s.get("display_text", "")
            cut["title"] = s.get("emoji", "") + " " + s.get("subtitle", "")
            cut["callout_type"] = "info"
            cut["accentColor"] = THEME_CONFIG["accentColor"]

        elif scene_type == "stat_card":
            cut["type"] = "stat_card"
            cut["stat"] = str(s.get("stat", "1"))
            cut["subtitle"] = s.get("stat_subtitle", s.get("display_text", ""))
            cut["accentColor"] = THEME_CONFIG["accentColor"]

        elif scene_type == "hero_title":
            cut["type"] = "hero_title"
            cut["text"] = s.get("display_text", "")
            cut["heroSubtitle"] = s.get("subtitle", "")

        else:
            cut["type"] = "text_card"
            cut["text"] = s.get("display_text", "")

        if not vid_path:
            cut.pop("backgroundVideo", None)
            cut.pop("backgroundVideoStart", None)
            cut["source"] = ""
            cut["backgroundColor"] = THEME_CONFIG["surfaceColor"]

        cuts.append(cut)

        # Section title overlay
        overlays.append({
            "type": "section_title",
            "text": s.get("label", ""),
            "subtitle": s.get("subtitle", ""),
            "accentColor": THEME_CONFIG["accentColor"],
            "position": "top-left",
            "in_seconds": current_t,
            "out_seconds": current_t + dur,
        })

        current_t += dur

    edit_decisions = {
        "render_runtime": "remotion",
        "renderer_family": "explainer-teacher",
        "cuts": cuts,
        "overlays": overlays,
        "themeConfig": THEME_CONFIG,
        "metadata": {
            "project": "ai-generated-kids",
            "pipeline": "ai-animated-explainer",
            "topic": "Dynamic AI Topic",
            "total_duration": total_duration,
            "renderer_family": "explainer-teacher",
        },
    }

    ed_path = PROJECT_DIR / "artifacts" / "edit_decisions_v2.json"
    ed_path.write_text(
        json.dumps(edit_decisions, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log("EDIT", f"✓ edit_decisions saved: {ed_path}")
    return edit_decisions


# ---------------------------------------------------------------------------
# STEP 4: Render via Remotion Node API
# ---------------------------------------------------------------------------
def step4_render_remotion(edit_decisions):
    log("COMPOSE", "Rendering video using Remotion Node API...")
    final_output = PROJECT_DIR / "renders" / "ai-generated-kids-v2.mp4"

    if not shutil.which("node"):
        raise RuntimeError("Node.js is not installed! Cannot run Remotion.")

    composer_dir = PROJECT_ROOT / "remotion-composer"
    api_script = composer_dir / "remotion_render_api.mjs"
    if not api_script.exists():
        raise RuntimeError("remotion_render_api.mjs missing from remotion-composer directory.")

    props_path = Path(tempfile.gettempdir()) / "remotion_ai_kids_props.json"
    props_path.write_text(
        json.dumps(edit_decisions, ensure_ascii=False), encoding="utf-8"
    )

    cmd = ["node", str(api_script), str(props_path), str(final_output)]
    log("COMPOSE", "  Running Remotion...")
    r = subprocess.run(cmd, cwd=str(composer_dir), capture_output=False, text=True)

    try:
        props_path.unlink()
    except Exception:
        pass

    if r.returncode != 0 or not final_output.exists():
        raise RuntimeError(f"Remotion failed with exit code {r.returncode}")

    size_mb = final_output.stat().st_size / 1024 / 1024
    log("COMPOSE", f"✓ Final video generated: {final_output} ({size_mb:.1f} MB)")
    return str(final_output)


def main():
    print("=" * 65)
    print("OpenMontage - AI Generated Kids Video")
    print("AI Model : Groq Llama-3-70b")
    print("Runtime  : Remotion (animated text cards over video)")
    print("Pipeline : No hardcoded scenes, fully dynamic")
    print("=" * 65)

    if not os.environ.get("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY not set in .env")
        sys.exit(1)
    if not os.environ.get("PEXELS_API_KEY"):
        print("ERROR: PEXELS_API_KEY not set in .env")
        sys.exit(1)

    # DUMMY LECTURE ABOUT PLANTS (Arabic)
    # The prompt explicitly asks the AI to not hardcode it, but process this specific text dynamically.
    lecture_text = """
    النباتات كائنات حية تتنفس وتتغذى وتنمو. تبدأ رحلة النبات من بذرة صغيرة نزرعها في التربة.
    تحتاج البذرة إلى الماء وأشعة الشمس لتكبر وتصبح نبتة صغيرة. 
    وبفضل عملية البناء الضوئي، تستخدم الأوراق الخضراء ضوء الشمس لصنع الغذاء.
    بمرور الوقت، تكبر النبتة وتصبح شجرة كبيرة ومفيدة تعطينا الأكسجين لنتنفس.
    """

    t0 = time.time()

    # 1. AI thinking
    scenes = step1_generate_script(lecture_text)

    # 2. Get videos
    video_files = step2_video_clips(scenes)

    # 3. Build decisions
    edit_decisions = step3_build_edit_decisions(scenes, video_files)

    # 4. Render
    final_video = step4_render_remotion(edit_decisions)

    elapsed = time.time() - t0
    total_duration = edit_decisions["metadata"]["total_duration"]
    print()
    print("=" * 65)
    print(f"PIPELINE COMPLETE in {elapsed:.0f}s")
    print(f"  Output : {final_video}")
    print(f"  Scenes : {len(scenes)}")
    print(f"  Duration: ~{total_duration}s")
    print("=" * 65)


if __name__ == "__main__":
    main()
