"""
OpenMontage - Egyptian Kids Video Production Script
Executive Producer driving the animated-explainer pipeline.

Topic: Why is the sky blue? (leh el sama zaraa?)
Audience: Egyptian children 6-12 years old
Language: Egyptian Arabic (Ammiya) per prompts/egyptian_kids.txt
Pipeline: animated-explainer -> Pexels video clips + ElevenLabs TTS + ElevenLabs Music + FFmpeg compose
"""

import io
import json
import os
import sys
import time
from pathlib import Path

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

PROJECT_DIR = PROJECT_ROOT / "projects" / "egyptian-kids-sky"
PROJECT_DIR.mkdir(parents=True, exist_ok=True)
(PROJECT_DIR / "artifacts").mkdir(exist_ok=True)
(PROJECT_DIR / "assets" / "audio").mkdir(parents=True, exist_ok=True)
(PROJECT_DIR / "assets" / "video").mkdir(parents=True, exist_ok=True)
(PROJECT_DIR / "assets" / "music").mkdir(parents=True, exist_ok=True)
(PROJECT_DIR / "renders").mkdir(exist_ok=True)

def log(stage, msg):
    print(f"[EP][{stage}] {msg}")

# ────────────────────────────────────────────────
# SCRIPT — Egyptian Arabic, children, sky topic
# ────────────────────────────────────────────────
SCRIPT_SECTIONS = [
    {
        "id": "s1",
        "label": "Intro - Hook",
        "text": "يسلام! إيه رأيك لو سألتك: ليه السما لونها أزرق؟ هتقولي إيه؟",
        "start_seconds": 0,
        "end_seconds": 6,
        "pexels_query": "blue sky clouds egypt",
    },
    {
        "id": "s2",
        "label": "Fun Fact 1 - Light rays",
        "text": "الشمس بتبعتلنا ضوء، وده الضوء مش بس أبيض! ده فيه كل ألوان قوس قزح جوّاه!",
        "start_seconds": 6,
        "end_seconds": 14,
        "pexels_query": "sunlight rainbow prism colors",
    },
    {
        "id": "s3",
        "label": "Fun Fact 2 - Scattering",
        "text": "لما الضوء بيدخل الجو، بيلاقي كتير من الجزيئات الصغيرة جداً. اللون الأزرق بيتشتت أكتر من باقي الألوان، فبييجي لعينينا من كل الاتجاهات!",
        "start_seconds": 14,
        "end_seconds": 25,
        "pexels_query": "atmosphere sky light scattering nature",
    },
    {
        "id": "s4",
        "label": "Fun Fact 3 - Sunset",
        "text": "ولذلك وقت الغروب، السما بتبقى برتقالية وحمرا! لأن الضوء بيسافر مسافة أطول في الجو ومفيش أزرق وصلنا!",
        "start_seconds": 25,
        "end_seconds": 35,
        "pexels_query": "sunset orange red sky egypt",
    },
    {
        "id": "s5",
        "label": "Outro",
        "text": "إذن السما زرقا عشان الضوء الأزرق بيتشتت أكتر من غيره! دلوقتي عارفين السر! شاركوا الكلام ده مع أصحابكم!",
        "start_seconds": 35,
        "end_seconds": 45,
        "pexels_query": "happy children egypt school learning",
    },
]

TOTAL_DURATION = 45  # seconds

def step1_generate_narration():
    """Generate TTS narration using gTTS (free, supports Arabic)."""
    log("ASSETS", "Generating narration audio with gTTS (free Arabic TTS)...")
    
    try:
        from gtts import gTTS
    except ImportError:
        raise RuntimeError("gTTS not installed. Run: pip install gtts")
    
    audio_files = {}
    
    for section in SCRIPT_SECTIONS:
        out_path = PROJECT_DIR / "assets" / "audio" / f"{section['id']}.mp3"
        
        if out_path.exists():
            log("ASSETS", f"  {section['id']} - already exists, skipping")
            audio_files[section['id']] = str(out_path)
            continue
        
        log("ASSETS", f"  Generating {section['id']} ({len(section['text'])} chars)...")
        
        try:
            # ar = Arabic, slow=False for normal pace
            tts = gTTS(text=section["text"], lang="ar", slow=False)
            tts.save(str(out_path))
            audio_files[section['id']] = str(out_path)
            log("ASSETS", f"  ✓ {section['id']} saved (free via gTTS)")
        except Exception as e:
            log("ASSETS", f"  ✗ gTTS failed for {section['id']}: {e}")
            raise RuntimeError(f"gTTS failed for {section['id']}: {e}")
        
        time.sleep(0.5)  # Be nice to the free service
    
    log("ASSETS", "Narration done (gTTS - free).")
    return audio_files


def step2_fetch_video_clips():
    """Download Pexels video clips for each section."""
    log("ASSETS", "Fetching Pexels stock video clips...")
    from tools.video.pexels_video import PexelsVideo
    
    pexels = PexelsVideo()
    video_files = {}
    
    for section in SCRIPT_SECTIONS:
        out_path = PROJECT_DIR / "assets" / "video" / f"{section['id']}.mp4"
        
        if out_path.exists():
            log("ASSETS", f"  {section['id']} - already exists, skipping")
            video_files[section['id']] = str(out_path)
            continue
        
        log("ASSETS", f"  Searching Pexels: '{section['pexels_query']}'...")
        
        result = pexels.execute({
            "query": section["pexels_query"],
            "orientation": "landscape",
            "size": "medium",
            "min_duration": int((section["end_seconds"] - section["start_seconds"]) * 0.8),
            "per_page": 5,
            "preferred_quality": "hd",
            "output_path": str(out_path),
        })
        
        if result.success:
            video_files[section['id']] = str(out_path)
            log("ASSETS", f"  ✓ {section['id']} → {result.data.get('duration_seconds')}s clip by {result.data.get('user')}")
        else:
            log("ASSETS", f"  ✗ Pexels failed for {section['id']}: {result.error}")
            log("ASSETS", f"    Trying fallback query: 'sky nature'")
            # Fallback
            result2 = pexels.execute({
                "query": "sky nature blue",
                "orientation": "landscape",
                "size": "medium",
                "per_page": 3,
                "preferred_quality": "hd",
                "output_path": str(out_path),
            })
            if result2.success:
                video_files[section['id']] = str(out_path)
                log("ASSETS", f"  ✓ {section['id']} fallback saved")
            else:
                raise RuntimeError(f"Pexels failed for {section['id']}: {result.error}")
        
        time.sleep(0.3)
    
    log("ASSETS", "Video clips done.")
    return video_files


def step3_generate_music():
    """Generate/fetch background music. Tries ElevenLabs, falls back to Pixabay."""
    log("ASSETS", "Getting background music...")
    music_path = PROJECT_DIR / "assets" / "music" / "background.mp3"
    
    if music_path.exists():
        log("ASSETS", "Music already exists, skipping.")
        return str(music_path)
    
    # Try ElevenLabs music gen first
    from tools.audio.music_gen import MusicGen
    music = MusicGen()
    
    result = music.execute({
        "prompt": "cheerful upbeat children educational music, Egyptian folk instruments, oud and tabla, playful and curious, instrumental, kids learning show",
        "duration_seconds": TOTAL_DURATION + 5,
        "output_path": str(music_path),
    })
    
    if result.success:
        log("ASSETS", f"✓ Music generated via ElevenLabs (~${result.cost_usd:.4f})")
        return str(music_path)
    
    log("ASSETS", f"  ElevenLabs music failed: {result.error}")
    log("ASSETS", "  Trying Pixabay music fallback...")
    
    # Fallback: Pixabay free music
    try:
        from tools.audio.pixabay_music import PixabayMusic
        pm = PixabayMusic()
        if str(pm.get_status()) == 'ToolStatus.AVAILABLE':
            r2 = pm.execute({
                "query": "children educational happy",
                "output_path": str(music_path),
            })
            if r2.success:
                log("ASSETS", "✓ Music fetched from Pixabay (free)")
                return str(music_path)
            log("ASSETS", f"  Pixabay music also failed: {r2.error}")
    except Exception as e:
        log("ASSETS", f"  Pixabay music error: {e}")
    
    log("ASSETS", "  Proceeding without background music.")
    return None


def step4_mix_audio(audio_files, music_path):
    """Mix narration + music using AudioMixer."""
    log("EDIT", "Mixing narration and music...")
    mixed_path = PROJECT_DIR / "assets" / "audio" / "mixed_final.mp3"
    
    if mixed_path.exists():
        log("EDIT", "Mixed audio already exists, skipping.")
        return str(mixed_path)
    
    from tools.audio.audio_mixer import AudioMixer
    mixer = AudioMixer()
    
    # Build narration tracks with timing
    narration_tracks = []
    for section in SCRIPT_SECTIONS:
        if section["id"] in audio_files:
            narration_tracks.append({
                "path": audio_files[section["id"]],
                "start_seconds": section["start_seconds"],
                "volume": 1.0,
            })
    
    mix_inputs = {
        "operation": "mix",
        "output_path": str(mixed_path),
        "duration_seconds": TOTAL_DURATION,
        "tracks": narration_tracks,
    }
    
    if music_path and Path(music_path).exists():
        mix_inputs["tracks"].append({
            "path": music_path,
            "start_seconds": 0,
            "volume": 0.15,  # Low music under narration
            "loop": True,
        })
    
    result = mixer.execute(mix_inputs)
    
    if result.success:
        log("EDIT", f"✓ Audio mixed: {mixed_path}")
        return str(mixed_path)
    else:
        log("EDIT", f"✗ Mix failed: {result.error}")
        # Return first narration file as fallback
        if narration_tracks:
            log("EDIT", "  Using first narration track as fallback.")
            return narration_tracks[0]["path"]
        return None


def step5_compose_video(video_files, mixed_audio_path):
    """Compose final video using FFmpeg via VideoCompose."""
    log("COMPOSE", "Composing final video with FFmpeg...")
    output_path = PROJECT_DIR / "renders" / "egyptian-kids-sky.mp4"
    
    if output_path.exists():
        log("COMPOSE", f"Output already exists: {output_path}")
        return str(output_path)
    
    from tools.video.video_compose import VideoCompose
    composer = VideoCompose()
    
    # Build cuts from video files
    cuts = []
    for section in SCRIPT_SECTIONS:
        if section["id"] not in video_files:
            log("COMPOSE", f"  ✗ Missing video for {section['id']}, skipping cut")
            continue
        
        duration = section["end_seconds"] - section["start_seconds"]
        cuts.append({
            "source": video_files[section["id"]],
            "in_seconds": 0,
            "out_seconds": duration,
            "label": section["label"],
        })
    
    edit_decisions = {
        "render_runtime": "ffmpeg",
        "cuts": cuts,
        "metadata": {
            "project": "egyptian-kids-sky",
            "total_duration": TOTAL_DURATION,
        }
    }
    
    result = composer.execute({
        "operation": "compose",
        "edit_decisions": edit_decisions,
        "output_path": str(output_path),
        "audio_path": mixed_audio_path,
        "codec": "libx264",
        "crf": 23,
        "preset": "medium",
    })
    
    if result.success:
        size_mb = output_path.stat().st_size / 1024 / 1024
        log("COMPOSE", f"✓ Video composed: {output_path} ({size_mb:.1f} MB)")
        return str(output_path)
    else:
        log("COMPOSE", f"✗ Compose failed: {result.error}")
        raise RuntimeError(f"Video compose failed: {result.error}")


def main():
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

    print("=" * 60)
    print("OpenMontage - Egyptian Kids Video Pipeline")
    print("Topic: Leh el sama zaraa? (Why is the sky blue?)")
    print(f"Project dir: {PROJECT_DIR}")
    print("=" * 60)
    
    # Only Pexels is strictly required; gTTS is free (no key needed)
    if not os.environ.get("PEXELS_API_KEY"):
        print("ERROR: PEXELS_API_KEY not set in .env")
        sys.exit(1)
    
    start_time = time.time()
    
    # Stage 1: Narration
    audio_files = step1_generate_narration()
    
    # Stage 2: Video clips
    video_files = step2_fetch_video_clips()
    
    # Stage 3: Music
    music_path = step3_generate_music()
    
    # Stage 4: Mix audio
    mixed_audio = step4_mix_audio(audio_files, music_path)
    
    # Stage 5: Compose
    final_video = step5_compose_video(video_files, mixed_audio)
    
    elapsed = time.time() - start_time
    print()
    print("=" * 60)
    print(f"✓ PIPELINE COMPLETE in {elapsed:.0f}s")
    print(f"  Output: {final_video}")
    print("=" * 60)
    
    # Save asset manifest
    manifest = {
        "project": "egyptian-kids-sky",
        "pipeline": "animated-explainer",
        "topic": "Leh el sama zaraa? (Why is the sky blue?)",
        "language": "Egyptian Arabic (Ammiya)",
        "total_duration_seconds": TOTAL_DURATION,
        "audio_files": audio_files,
        "video_files": video_files,
        "music_path": music_path,
        "mixed_audio": mixed_audio,
        "final_video": final_video,
    }
    manifest_path = PROJECT_DIR / "artifacts" / "asset_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    log("PUBLISH", f"Manifest saved: {manifest_path}")


if __name__ == "__main__":
    main()
