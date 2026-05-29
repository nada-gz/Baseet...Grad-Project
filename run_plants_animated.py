"""
OpenMontage - Egyptian Kids Plants Video (Animated Explainer)
=============================================================
Topic : el nabat w ezay bitkbar (How do plants grow?)
Audience : Egyptian children 6-12
Language : Egyptian Arabic (Ammiya)
Runtime : Remotion (animated text + video composite)
Pipeline : gTTS narration -> Pexels video -> Remotion render
           Each scene = real video clip in background + animated Arabic text overlay
"""

import io
import json
import os
import sys
import time
from pathlib import Path

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

PROJECT_DIR = PROJECT_ROOT / "projects" / "egyptian-kids-plants"
for sub in ["artifacts", "assets/audio", "assets/video", "assets/music", "renders"]:
    (PROJECT_DIR / sub).mkdir(parents=True, exist_ok=True)


def log(stage, msg):
    print(f"[EP][{stage}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Script — Egyptian Arabic, plants topic, kids style
# Each section has:
#   text        : Arabic narration
#   display_text: Short Arabic text shown ON SCREEN as animated card
#   emoji       : decorative (used in callout)
#   pexels_query: Stock video query
#   duration    : seconds this scene runs
# ---------------------------------------------------------------------------
SECTIONS = [
    {
        "id": "s1",
        "label": "Hook",
        "text": "يسلام! عارفين إيه أحسن حاجة في العالم؟ النبات! بس إزاي الشجرة الكبيرة دي بدأت من بذرة صغيرة؟",
        "display_text": "إزاي الشجرة بتكبر؟",
        "subtitle": "How does a tree grow?",
        "emoji": "🌱",
        "pexels_query": "green plant growing time lapse nature",
        "scene_type": "text_card",       # animated text card over video bg
        "duration": 8,
    },
    {
        "id": "s2",
        "label": "Fact 1 - Seeds",
        "text": "كل شجرة كبيرة بدأت من بذرة صغيرة! البذرة فيها كل المعلومات اللي النبات محتاجها عشان ينمو!",
        "display_text": "البذرة = بداية الحياة",
        "subtitle": "Every plant starts from a seed",
        "emoji": "🌰",
        "pexels_query": "seeds soil germination plant sprout",
        "scene_type": "callout",
        "duration": 9,
    },
    {
        "id": "s3",
        "label": "Fact 2 - Water & Sun",
        "text": "النبات محتاج تلت حاجات عشان يكبر: ميه، وشمس، وتراب كويس! من غير واحدة منهم، النبات مش هيطلع!",
        "display_text": "ميه + شمس + تراب = نبات",
        "subtitle": "Water + Sunlight + Soil = Plant",
        "emoji": "☀️",
        "pexels_query": "watering plants sunlight garden",
        "scene_type": "text_card",
        "duration": 10,
    },
    {
        "id": "s4",
        "label": "Fact 3 - Photosynthesis",
        "text": "النبات بيعمل أكله بنفسه! بياخد ضوء الشمس والميه ويحولهم لسكر وأكسجين. ده بنسميه البناء الضوئي!",
        "display_text": "النبات بيعمل أكله بنفسه!",
        "subtitle": "Plants make their own food",
        "emoji": "🍃",
        "pexels_query": "photosynthesis green leaves sunlight close up",
        "scene_type": "callout",
        "duration": 11,
    },
    {
        "id": "s5",
        "label": "Fun Fact - Biggest Tree",
        "text": "تعرفوا إن في شجرة عمرها أكتر من خمستالاف سنة؟ وفي أشجار بتوصل ارتفاعها لمية متر! يعني تقريبا زي عمارة من تلاتين دور!",
        "display_text": "أكبر شجرة: 5000 سنة!",
        "subtitle": "Oldest tree: 5,000 years old!",
        "emoji": "🌳",
        "pexels_query": "giant ancient tree forest massive",
        "scene_type": "stat_card",
        "stat": "5000",
        "stat_subtitle": "سنة عمر الشجرة الأقدم",
        "duration": 9,
    },
    {
        "id": "s6",
        "label": "Outro",
        "text": "النبات حياة! اتعلمنا إزاي بيبدأ من بذرة وبياخد ميه وشمس ويعمل أكله بنفسه. دلوقتي زرعوا بذرة في البيت وشوفوا السحر بعينيكم!",
        "display_text": "ازرع بذرة النهارده!",
        "subtitle": "Plant a seed today!",
        "emoji": "🪴",
        "pexels_query": "child planting seed garden educational",
        "scene_type": "hero_title",
        "duration": 10,
    },
]

TOTAL_DURATION = sum(s["duration"] for s in SECTIONS)  # ~57 seconds

# Theme: Lush green kids palette
THEME_CONFIG = {
    "primaryColor": "#2D9E4F",       # fresh green
    "accentColor": "#F6C026",        # sunny yellow
    "backgroundColor": "#0D2416",    # deep forest dark
    "surfaceColor": "#1A3D25",       # mid-dark green
    "textColor": "#E8F5E9",          # near-white
    "mutedTextColor": "#A5D6A7",     # light green
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
# STEP 1: Generate Arabic narration via gTTS
# ---------------------------------------------------------------------------
def step1_narration():
    log("ASSETS", "Generating Arabic narration with gTTS...")
    try:
        from gtts import gTTS
    except ImportError:
        raise RuntimeError("Install gTTS: pip install gtts")

    audio_files = {}
    for s in SECTIONS:
        out = PROJECT_DIR / "assets" / "audio" / f"{s['id']}.mp3"
        if out.exists():
            log("ASSETS", f"  {s['id']} exists, skip")
            audio_files[s["id"]] = str(out)
            continue
        log("ASSETS", f"  {s['id']}: generating ({len(s['text'])} chars)...")
        gTTS(text=s["text"], lang="ar", slow=False).save(str(out))
        audio_files[s["id"]] = str(out)
        log("ASSETS", f"  ✓ {s['id']} saved")
        time.sleep(0.5)

    log("ASSETS", f"Narration done ({len(audio_files)} files).")
    return audio_files


# ---------------------------------------------------------------------------
# STEP 2: Concatenate all narration into one mixed audio file
#         (narration segments laid out at correct timestamps)
# ---------------------------------------------------------------------------
def step2_mix_narration(audio_files):
    """Stitch narration segments together with silence padding using ffmpeg."""
    log("EDIT", "Stitching narration into single timeline...")
    mixed = PROJECT_DIR / "assets" / "audio" / "narration_full.mp3"
    if mixed.exists():
        log("EDIT", "Narration full mix exists, skip.")
        return str(mixed)

    import subprocess

    # Build ffmpeg filter_complex to lay segments at correct timestamps
    inputs = []
    filter_parts = []
    current_t = 0.0

    for i, s in enumerate(SECTIONS):
        aid = s["id"]
        if aid not in audio_files:
            continue
        inputs += ["-i", audio_files[aid]]
        filter_parts.append(
            f"[{i}:a]adelay={int(current_t * 1000)}|{int(current_t * 1000)}[a{i}]"
        )
        current_t += s["duration"]

    n = len(filter_parts)
    mix_inputs = "".join(f"[a{i}]" for i in range(n))
    filter_complex = (
        ";".join(filter_parts)
        + f";{mix_inputs}amix=inputs={n}:duration=longest:normalize=0[out]"
    )

    cmd = (
        ["ffmpeg", "-y"]
        + inputs
        + [
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-acodec", "libmp3lame",
            "-ar", "44100",
            "-ac", "2",
            str(mixed),
        ]
    )
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log("EDIT", f"  ffmpeg stderr: {result.stderr[-400:]}")
        raise RuntimeError("Narration mix failed")

    log("EDIT", f"✓ Narration mixed: {mixed}")
    return str(mixed)


# ---------------------------------------------------------------------------
# STEP 3: Get background music (Pixabay free)
# ---------------------------------------------------------------------------
def step3_music():
    log("ASSETS", "Getting background music...")
    music = PROJECT_DIR / "assets" / "music" / "background.mp3"
    if music.exists():
        log("ASSETS", "Music exists, skip.")
        return str(music)

    try:
        from tools.audio.pixabay_music import PixabayMusic
        pm = PixabayMusic()
        if "available" in str(pm.get_status()).lower():
            r = pm.execute({
                "query": "children happy nature educational",
                "output_path": str(music),
            })
            if r.success:
                log("ASSETS", "✓ Music from Pixabay")
                return str(music)
            log("ASSETS", f"  Pixabay failed: {r.error}")
    except Exception as e:
        log("ASSETS", f"  Pixabay error: {e}")

    log("ASSETS", "  No music available, proceeding without.")
    return None


# ---------------------------------------------------------------------------
# STEP 4: Fetch Pexels background video clips
# ---------------------------------------------------------------------------
def step4_video_clips():
    log("ASSETS", "Fetching Pexels video clips...")
    from tools.video.pexels_video import PexelsVideo
    pexels = PexelsVideo()

    video_files = {}
    for s in SECTIONS:
        out = PROJECT_DIR / "assets" / "video" / f"{s['id']}.mp4"
        if out.exists():
            log("ASSETS", f"  {s['id']} exists, skip")
            video_files[s["id"]] = str(out)
            continue

        log("ASSETS", f"  Searching: '{s['pexels_query']}'...")
        r = pexels.execute({
            "query": s["pexels_query"],
            "orientation": "landscape",
            "size": "medium",
            "min_duration": max(4, s["duration"] - 3),
            "per_page": 5,
            "preferred_quality": "hd",
            "output_path": str(out),
        })

        if r.success:
            video_files[s["id"]] = str(out)
            log("ASSETS", f"  ✓ {s['id']}: {r.data.get('duration_seconds')}s by {r.data.get('user')}")
        else:
            # Fallback
            log("ASSETS", f"  Trying fallback: 'nature green plants'")
            r2 = pexels.execute({
                "query": "nature green plants",
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

    log("ASSETS", f"Video clips done ({len(video_files)} files).")
    return video_files


# ---------------------------------------------------------------------------
# STEP 5: Copy assets to temp dir (no spaces) + Build Remotion edit_decisions
# ---------------------------------------------------------------------------
TEMP_ASSETS = Path("C:/Users/zeina/remotion_plants_assets")

def step5_build_edit_decisions(audio_files, video_files, narration_path, music_path):
    """Build edit_decisions for Remotion — copies all media to a no-space temp dir."""
    log("EDIT", "Copying assets to temp dir (no spaces for Remotion)...")
    TEMP_ASSETS.mkdir(parents=True, exist_ok=True)

    import shutil as _shutil

    # Copy video files to temp dir
    temp_video = {}
    for sid, vpath in video_files.items():
        dest = TEMP_ASSETS / f"v_{sid}.mp4"
        if not dest.exists():
            _shutil.copy2(vpath, dest)
        temp_video[sid] = str(dest)

    log("EDIT", f"  Copied {len(temp_video)} video files to {TEMP_ASSETS}")
    log("EDIT", "Building Remotion edit_decisions...")

    cuts = []
    overlays = []
    current_t = 0.0

    for s in SECTIONS:
        dur = s["duration"]
        scene_type = s.get("scene_type", "text_card")
        vid_path = temp_video.get(s["id"])

        cut = {
            "id": s["id"],
            "source": vid_path if vid_path else "",
            "in_seconds": current_t,
            "out_seconds": current_t + dur,
            "backgroundOverlay": 0.55,
        }

        # Use video as background for text component scenes
        if vid_path:
            cut["backgroundVideo"] = vid_path
            cut["backgroundVideoStart"] = 0

        # Build scene type with animated Arabic text
        if scene_type == "text_card":
            cut["type"] = "text_card"
            cut["text"] = s["display_text"]
            cut["fontSize"] = 90
            cut["color"] = THEME_CONFIG["textColor"]

        elif scene_type == "callout":
            cut["type"] = "callout"
            cut["text"] = s["display_text"]
            cut["title"] = s.get("emoji", "") + " " + s["subtitle"]
            cut["callout_type"] = "info"
            cut["accentColor"] = THEME_CONFIG["accentColor"]

        elif scene_type == "stat_card":
            cut["type"] = "stat_card"
            cut["stat"] = s.get("stat", "")
            cut["subtitle"] = s.get("stat_subtitle", s["display_text"])
            cut["accentColor"] = THEME_CONFIG["accentColor"]

        elif scene_type == "hero_title":
            cut["type"] = "hero_title"
            cut["text"] = s["display_text"]
            cut["heroSubtitle"] = s["subtitle"]

        else:
            cut["type"] = "text_card"
            cut["text"] = s["display_text"]

        if not vid_path:
            cut.pop("backgroundVideo", None)
            cut.pop("backgroundVideoStart", None)
            cut["source"] = ""
            cut["backgroundColor"] = THEME_CONFIG["surfaceColor"]

        cuts.append(cut)

        # Section title overlay
        overlays.append({
            "type": "section_title",
            "text": s["label"],
            "subtitle": s["subtitle"],
            "accentColor": THEME_CONFIG["accentColor"],
            "position": "top-left",
            "in_seconds": current_t,
            "out_seconds": current_t + dur,
        })

        current_t += dur

    # NOTE: NO audio block in Remotion props — Chromium can't load mp3 via file://
    # Audio will be muxed in by FFmpeg after Remotion renders the silent video.
    edit_decisions = {
        "render_runtime": "remotion",
        "renderer_family": "explainer-teacher",
        "cuts": cuts,
        "overlays": overlays,
        "themeConfig": THEME_CONFIG,
        "metadata": {
            "project": "egyptian-kids-plants",
            "pipeline": "animated-explainer",
            "topic": "How do plants grow? (Egyptian Arabic)",
            "total_duration": TOTAL_DURATION,
            "renderer_family": "explainer-teacher",
        },
    }

    ed_path = PROJECT_DIR / "artifacts" / "edit_decisions.json"
    ed_path.write_text(
        json.dumps(edit_decisions, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log("EDIT", f"✓ edit_decisions saved: {ed_path}")
    return edit_decisions, narration_path, music_path


# ---------------------------------------------------------------------------
# STEP 6: Render via Remotion Node API (bypasses Windows --props CLI issue)
# ---------------------------------------------------------------------------
def step6_render_remotion(edit_decisions, narration_path, music_path):
    log("COMPOSE", "Rendering via Remotion Node API (animated text + video)...")
    silent_output = PROJECT_DIR / "renders" / "egyptian-kids-plants-silent.mp4"
    final_output = PROJECT_DIR / "renders" / "egyptian-kids-plants.mp4"

    if final_output.exists():
        log("COMPOSE", f"Output exists: {final_output}")
        return str(final_output)

    import shutil, subprocess, tempfile

    if not shutil.which("node"):
        log("COMPOSE", "  node not found! Falling back to FFmpeg.")
        return _fallback_ffmpeg(edit_decisions, final_output, narration_path)

    composer_dir = PROJECT_ROOT / "remotion-composer"
    api_script = composer_dir / "remotion_render_api.mjs"
    if not api_script.exists():
        log("COMPOSE", "  remotion_render_api.mjs missing, falling back to FFmpeg.")
        return _fallback_ffmpeg(edit_decisions, final_output, narration_path)

    # Write props to temp file (no BOM, no space in path)
    props_path = Path(tempfile.gettempdir()) / "remotion_plants_props.json"
    props_path.write_text(
        json.dumps(edit_decisions, ensure_ascii=False), encoding="utf-8"
    )

    # Remotion renders silent video (no audio in props — avoids file:// space issue)
    cmd = ["node", str(api_script), str(props_path), str(silent_output)]
    log("COMPOSE", "  Running Remotion (silent pass)...")
    r = subprocess.run(cmd, cwd=str(composer_dir), capture_output=False, text=True)

    try:
        props_path.unlink()
    except Exception:
        pass

    if r.returncode != 0 or not silent_output.exists():
        log("COMPOSE", f"  Remotion failed (exit={r.returncode}), falling back to FFmpeg.")
        if silent_output.exists():
            silent_output.unlink()
        return _fallback_ffmpeg(edit_decisions, final_output, narration_path)

    log("COMPOSE", "  ✓ Remotion silent render done, muxing audio...")

    # Mix narration (volume 1.0) + music (volume 0.12) + mux into video
    audio_inputs = []
    audio_filter = ""

    if narration_path and Path(narration_path).exists():
        audio_inputs += ["-i", narration_path]
    if music_path and Path(music_path).exists():
        audio_inputs += ["-i", music_path]

    n_audio = len(audio_inputs) // 2

    if n_audio == 0:
        # No audio — just rename silent video
        shutil.copy2(str(silent_output), str(final_output))
        silent_output.unlink()
    elif n_audio == 1:
        # Single audio track
        mux_cmd = [
            "ffmpeg", "-y",
            "-i", str(silent_output),
        ] + audio_inputs + [
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac",
            "-shortest", str(final_output),
        ]
        subprocess.run(mux_cmd, check=True, capture_output=True)
        silent_output.unlink()
    else:
        # Narration + music mix
        mux_cmd = [
            "ffmpeg", "-y",
            "-i", str(silent_output),
        ] + audio_inputs + [
            "-filter_complex",
            f"[1:a]volume=1.0[narr];[2:a]volume=0.12[mus];[narr][mus]amix=inputs=2:duration=first[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            str(final_output),
        ]
        result = subprocess.run(mux_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            log("COMPOSE", f"  Audio mux failed: {result.stderr[-200:]}")
            # Fallback: just use narration only
            mux_cmd2 = [
                "ffmpeg", "-y",
                "-i", str(silent_output),
                "-i", narration_path,
                "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac", "-shortest",
                str(final_output),
            ]
            subprocess.run(mux_cmd2, check=True, capture_output=True)
        silent_output.unlink()

    size_mb = final_output.stat().st_size / 1024 / 1024
    log("COMPOSE", f"✓ Final video with audio: {final_output} ({size_mb:.1f} MB)")
    return str(final_output)


def _fallback_ffmpeg(edit_decisions, output, narration_path=None):
    """FFmpeg fallback: simple video concat + audio mix (no animated text)."""
    log("COMPOSE", "Using FFmpeg fallback (no animated text)...")
    from tools.video.video_compose import VideoCompose
    composer = VideoCompose()

    ffmpeg_cuts = []
    for cut in edit_decisions["cuts"]:
        src = cut.get("backgroundVideo") or cut.get("source", "")
        if src and Path(src).exists():
            dur = cut["out_seconds"] - cut["in_seconds"]
            ffmpeg_cuts.append({
                "source": src,
                "in_seconds": 0,
                "out_seconds": dur,
                "label": cut.get("id", ""),
            })

    if not ffmpeg_cuts:
        raise RuntimeError("No video sources for FFmpeg fallback")

    ffmpeg_ed = {
        "render_runtime": "ffmpeg",
        "cuts": ffmpeg_cuts,
        "metadata": edit_decisions.get("metadata", {}),
    }

    result = composer.execute({
        "operation": "compose",
        "edit_decisions": ffmpeg_ed,
        "output_path": str(output),
        "audio_path": narration_path,
        "codec": "libx264",
        "crf": 23,
        "preset": "medium",
    })

    if result.success:
        size_mb = output.stat().st_size / 1024 / 1024
        log("COMPOSE", f"✓ FFmpeg fallback: {output} ({size_mb:.1f} MB)")
        return str(output)
    else:
        raise RuntimeError(f"FFmpeg fallback failed: {result.error}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("=" * 65)
    print("OpenMontage - Egyptian Kids Plants (Animated Explainer)")
    print(f"Topic : How do plants grow? (Egyptian Arabic)")
    print(f"Runtime: Remotion (animated text cards over video)")
    print(f"Duration: ~{TOTAL_DURATION}s | Scenes: {len(SECTIONS)}")
    print(f"Project: {PROJECT_DIR}")
    print("=" * 65)

    if not os.environ.get("PEXELS_API_KEY"):
        print("ERROR: PEXELS_API_KEY not set in .env")
        sys.exit(1)

    t0 = time.time()

    # Stage 1: Narration
    audio_files = step1_narration()

    # Stage 2: Mix narration into single track
    narration_path = step2_mix_narration(audio_files)

    # Stage 3: Background music
    music_path = step3_music()

    # Stage 4: Video clips from Pexels
    video_files = step4_video_clips()

    # Stage 5: Build Remotion edit_decisions (assets copied to no-space temp)
    edit_decisions, narration_path, music_path = step5_build_edit_decisions(
        audio_files, video_files, narration_path, music_path
    )

    # Stage 6: Render (Remotion silent pass + FFmpeg audio mux)
    final_video = step6_render_remotion(edit_decisions, narration_path, music_path)

    elapsed = time.time() - t0
    print()
    print("=" * 65)
    print(f"PIPELINE COMPLETE in {elapsed:.0f}s")
    print(f"  Output : {final_video}")
    print(f"  Scenes : {len(SECTIONS)}")
    print(f"  Duration: ~{TOTAL_DURATION}s")
    print("=" * 65)

    # Save manifest
    manifest = {
        "project": "egyptian-kids-plants",
        "final_video": final_video,
        "audio_files": audio_files,
        "video_files": video_files,
        "narration_path": narration_path,
        "music_path": music_path,
        "total_duration_seconds": TOTAL_DURATION,
    }
    mp = PROJECT_DIR / "artifacts" / "asset_manifest.json"
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    log("PUBLISH", f"Manifest: {mp}")


if __name__ == "__main__":
    main()
