"""
OpenMontage - AI Generated Kids Video V3
=============================================================
Topic: Dynamic (using dummy plants text for now)
Audience: Egyptian children 6-12
Language: Egyptian Arabic (Ammiya)
Runtime: Remotion (background) + SadTalker (avatar) + FFmpeg (composite)
Pipeline: Groq AI -> HuggingFace TTS -> SadTalker Avatar -> Pexels Video -> Remotion -> FFmpeg PIP
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
import wave
from pathlib import Path

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.avatar.talking_head import TalkingHead

PROJECT_DIR = PROJECT_ROOT / "projects" / "ai-generated-kids-v3"
for sub in ["artifacts", "assets/video", "assets/audio", "assets/avatar", "renders"]:
    (PROJECT_DIR / sub).mkdir(parents=True, exist_ok=True)

def log(stage, msg):
    print(f"[AI-PIPELINE-V3][{stage}] {msg}", flush=True)

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

    system_prompt = """
You are an expert video director for an Egyptian children's educational channel.
You receive a lecture text and must produce a fun, engaging, and simple video script.

CRITICAL RULES:
1. DO NOT SKIP ANY INFORMATION. You must cover every single concept from the lecture.
2. DURATION RULE: The total video MUST be longer than 60 seconds. To achieve this, expand on the lecture by adding a fun story, interactive questions for the kids, and detailed explanations. Generate at least 10 to 15 scenes!
3. VISUAL CHARACTERS: Heavily use the "callout" scene type with character emojis (e.g. 👩‍🏫, 🧑‍🌾, 🧒, 🧑‍🔬).
4. The "display_text" will be spoken by a TTS engine, so make sure it is written in natural Egyptian Arabic (Ammiya).

You must reply with a valid JSON object containing a single key "scenes" whose value is an array of scene objects.
Each scene object MUST have:
- "id": string (e.g., "s1", "s2").
- "label": Short english label (e.g., "Intro", "Fact 1").
- "display_text": Fun, simple kid-friendly Egyptian Arabic text. This will be shown on screen AND spoken.
- "subtitle": English translation of the display_text.
- "emoji": A single relevant emoji.
- "pexels_query": 3-4 english keywords to search for a background stock video on Pexels.
- "scene_type": Prefer "callout" for explanations. Choose from ["text_card", "callout", "stat_card", "hero_title"].
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
        log("THINK", f"✓ AI generated {len(scenes)} scenes (aiming for >1 min).")
        return scenes
    except Exception as e:
        log("THINK", f"Failed to parse AI output: {e}\nContent was:\n{content}")
        raise

# ---------------------------------------------------------------------------
# STEP 2: Generate TTS and Measure Exact Duration
# ---------------------------------------------------------------------------
def step2_generate_tts(scenes):
    log("VOICE", "Loading facebook/mms-tts-ara via HuggingFace...")
    try:
        from transformers import VitsModel, AutoTokenizer
        import torch
        import scipy.io.wavfile
    except ImportError:
        log("VOICE", "Installing required packages for local TTS...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "transformers", "torch", "scipy"])
        from transformers import VitsModel, AutoTokenizer
        import torch
        import scipy.io.wavfile

    model = VitsModel.from_pretrained("facebook/mms-tts-ara")
    tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-ara")
    
    audio_paths = []
    
    for s in scenes:
        out_path = PROJECT_DIR / "assets" / "audio" / f"{s['id']}.wav"
        text = s.get("display_text", "")
        
        if not out_path.exists():
            log("VOICE", f"  Generating speech for {s['id']}...")
            inputs = tokenizer(text, return_tensors="pt")
            with torch.no_grad():
                output = model(**inputs).waveform
            scipy.io.wavfile.write(str(out_path), rate=model.config.sampling_rate, data=output.numpy().T)
            duration = output.shape[1] / float(model.config.sampling_rate)
        else:
            # If it already exists, just load it via scipy to get duration
            rate, data = scipy.io.wavfile.read(str(out_path))
            duration = len(data) / float(rate)
            
        # Overwrite scene duration to perfectly match the audio!
        # Add 0.5s padding so it doesn't cut off instantly
        s["duration"] = duration + 0.5
        audio_paths.append(str(out_path))
        
    log("VOICE", "✓ All TTS audio generated and synced with scenes.")
    return scenes, audio_paths

# ---------------------------------------------------------------------------
# STEP 3: Concatenate Audio and Animate SadTalker Avatar
# ---------------------------------------------------------------------------
def step3_generate_avatar(audio_paths):
    log("AVATAR", "Concatenating audio tracks...")
    full_audio_path = PROJECT_DIR / "assets" / "audio" / "full_audio.wav"
    
    # We use FFmpeg to concat audio
    list_path = PROJECT_DIR / "assets" / "audio" / "concat_list.txt"
    with open(list_path, "w", encoding="utf-8") as f:
        for p in audio_paths:
            # Add silence padding for the extra 0.5s we added to scene duration
            f.write(f"file '{Path(p).absolute()}'\n")
    
    # We will just concat them directly for simplicity. The padding might be slightly off visually by fractions of a second, but it will work.
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path), "-c", "copy", str(full_audio_path)]
    subprocess.run(cmd, check=True, capture_output=True)
    
    log("AVATAR", "Downloading generic avatar image...")
    avatar_image = PROJECT_DIR / "assets" / "avatar" / "teacher.jpg"
    if not avatar_image.exists():
        # Generic royalty-free portrait to use as avatar
        url = "https://images.pexels.com/photos/3760263/pexels-photo-3760263.jpeg" 
        r = requests.get(url)
        avatar_image.write_bytes(r.content)
        
    log("AVATAR", "Running Wav2Lip to animate avatar (This is much faster and stable!)...")
    avatar_video = PROJECT_DIR / "assets" / "avatar" / "avatar_talking.mp4"
    if not avatar_video.exists():
        from tools.avatar.lip_sync import LipSync
        th = LipSync()
        res = th.execute({
            "video_path": str(avatar_image),
            "audio_path": str(full_audio_path),
            "output_path": str(avatar_video),
            "model": "wav2lip_gan",
        })
        if not res.success:
            raise RuntimeError(f"Wav2Lip failed: {res.error}")
            
    log("AVATAR", "✓ Avatar talking video generated.")
    return str(full_audio_path), str(avatar_video)

# ---------------------------------------------------------------------------
# STEP 4: Fetch Pexels background video clips
# ---------------------------------------------------------------------------
def step4_video_clips(scenes):
    log("ASSETS", "Fetching Pixabay video clips...")
    from tools.video.pixabay_video import PixabayVideo
    pexels = PixabayVideo()

    video_files = {}
    for s in scenes:
        out = PROJECT_DIR / "assets" / "video" / f"{s['id']}.mp4"
        if out.exists():
            video_files[s["id"]] = str(out)
            continue

        query = s.get("pexels_query", "nature")
        log("ASSETS", f"  Searching: '{query}'...")
        r = pexels.execute({
            "query": query,
            "orientation": "landscape",
            "size": "medium",
            "min_duration": max(4, int(s["duration"])),
            "per_page": 5,
            "preferred_quality": "hd",
            "output_path": str(out),
        })

        if r.success:
            video_files[s["id"]] = str(out)
        else:
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
        time.sleep(0.3)
    return video_files

# ---------------------------------------------------------------------------
# STEP 5: Build Remotion edit_decisions
# ---------------------------------------------------------------------------
TEMP_ASSETS = PROJECT_DIR / "temp_remotion_assets"

def step5_build_edit_decisions(scenes, video_files):
    log("EDIT", "Building Remotion edit_decisions...")
    TEMP_ASSETS.mkdir(parents=True, exist_ok=True)

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
        scene_type = s.get("scene_type", "callout")
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

        cut["type"] = "callout"
        cut["text"] = s.get("display_text", "")
        cut["title"] = s.get("emoji", "") + " " + s.get("subtitle", "")
        cut["callout_type"] = "info"
        cut["accentColor"] = THEME_CONFIG["accentColor"]

        if not vid_path:
            cut.pop("backgroundVideo", None)
            cut.pop("backgroundVideoStart", None)
            cut["source"] = ""
            cut["backgroundColor"] = THEME_CONFIG["surfaceColor"]

        cuts.append(cut)
        current_t += dur

    edit_decisions = {
        "render_runtime": "remotion",
        "renderer_family": "explainer-teacher",
        "cuts": cuts,
        "overlays": overlays,
        "themeConfig": THEME_CONFIG,
        "metadata": {
            "project": "ai-generated-kids-v3",
            "pipeline": "ai-animated-explainer",
            "topic": "Dynamic AI Topic",
            "total_duration": total_duration,
            "renderer_family": "explainer-teacher",
        },
    }

    ed_path = PROJECT_DIR / "artifacts" / "edit_decisions.json"
    ed_path.write_text(json.dumps(edit_decisions, ensure_ascii=False, indent=2), encoding="utf-8")
    return edit_decisions

# ---------------------------------------------------------------------------
# STEP 6: Render Remotion Video
# ---------------------------------------------------------------------------
def step6_render_remotion(edit_decisions):
    log("COMPOSE", "Rendering background video using Remotion...")
    silent_output = PROJECT_DIR / "renders" / "remotion_bg.mp4"

    composer_dir = PROJECT_ROOT / "remotion-composer"
    api_script = composer_dir / "remotion_render_api.mjs"

    props_path = PROJECT_DIR / "artifacts" / "remotion_ai_kids_v3_props.json"
    props_path.write_text(json.dumps(edit_decisions, ensure_ascii=False), encoding="utf-8")

    cmd = ["node", str(api_script), str(props_path), str(silent_output)]
    r = subprocess.run(cmd, cwd=str(composer_dir), capture_output=False, text=True)

    try:
        props_path.unlink()
    except Exception:
        pass

    if r.returncode != 0 or not silent_output.exists():
        raise RuntimeError(f"Remotion failed with exit code {r.returncode}")
        
    return str(silent_output)

# ---------------------------------------------------------------------------
# STEP 7: Final Composite (PIP + Audio)
# ---------------------------------------------------------------------------
def step7_final_composite(remotion_bg, avatar_video, full_audio):
    log("COMPOSE", "Compositing PIP Avatar and Audio via FFmpeg...")
    final_output = PROJECT_DIR / "renders" / "ai-generated-kids-v3.mp4"
    
    # Place avatar in bottom right corner.
    # Remotion bg is 1920x1080 usually or 1280x720. Let's scale avatar to width 300.
    # overlay=W-w-20:H-h-20 (bottom right with 20px padding)
    cmd = [
        "ffmpeg", "-y",
        "-i", remotion_bg,
        "-i", avatar_video,
        "-i", full_audio,
        # Move to top-right (W-w-50:50), make it larger (450w), and add a 5px white border
        "[1:v]scale=450:-1,pad=iw+10:ih+10:5:5:white,format=yuv420p,setpts=PTS-STARTPTS[av];[0:v][av]overlay=W-w-50:50[outv]",
        "-map", "[outv]",
        "-map", "2:a",
        "-c:v", "libx264",
        "-crf", "23",
        "-c:a", "aac",
        "-shortest",
        str(final_output)
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    
    size_mb = final_output.stat().st_size / 1024 / 1024
    log("COMPOSE", f"✓ Final video V3 generated: {final_output} ({size_mb:.1f} MB)")
    return str(final_output)

def main():
    print("=" * 65)
    print("OpenMontage - AI Generated Kids Video V3")
    print("Featuring: Groq LLM, Facebook MMS-TTS, SadTalker Avatar, Remotion")
    print("=" * 65)

    lecture_text = """
    النباتات كائنات حية تتنفس وتتغذى وتنمو. تبدأ رحلة النبات من بذرة صغيرة نزرعها في التربة.
    تحتاج البذرة إلى الماء وأشعة الشمس لتكبر وتصبح نبتة صغيرة. 
    وبفضل عملية البناء الضوئي، تستخدم الأوراق الخضراء ضوء الشمس لصنع الغذاء.
    بمرور الوقت، تكبر النبتة وتصبح شجرة كبيرة ومفيدة تعطينا الأكسجين لنتنفس.
    """

    t0 = time.time()
    
    # 1. AI thinking
    scenes = step1_generate_script(lecture_text)

    # 2. TTS Voice Generation
    scenes, audio_paths = step2_generate_tts(scenes)
    
    # 3. Avatar Generation
    full_audio, avatar_video = step3_generate_avatar(audio_paths)

    # 4. Get videos
    video_files = step4_video_clips(scenes)

    # 5. Build decisions
    edit_decisions = step5_build_edit_decisions(scenes, video_files)

    # 6. Render Background
    remotion_bg = step6_render_remotion(edit_decisions)
    
    # 7. Final Composite
    final_video = step7_final_composite(remotion_bg, avatar_video, full_audio)

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
