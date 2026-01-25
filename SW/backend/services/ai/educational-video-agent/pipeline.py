import asyncio
import json
import re
import time
import subprocess
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from llm import QwenClient, plan_lesson, generate_code, fix_code
from tools.manim_executor import execute_manim_code
from tools.tts_generator import generate_audio
from tools.serp_image_retriever import get_image


# Fix Windows Unicode/emoji encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Output directory configuration - standardized paths in Grad-Project
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent  # Navigate to Grad-Project root
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "educational-videos"
TEMP_DIR = OUTPUT_DIR / "temp"
AUDIO_DIR = OUTPUT_DIR / "audio"
VIDEO_DIR = OUTPUT_DIR / "videos"

# Initialize Qwen client (reusable instance)
qwen_client = QwenClient()
SERPAPI_KEY = os.getenv('SERPAPI_KEY')

def extract_scene_name(code: str) -> str:
    match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\)', code)
    return match.group(1) if match else "Scene"


def merge_videos(segments: list, output_path: str = None) -> str:
    """Merge videos with audio using ffmpeg."""
    if not segments:
        print("✗ No segments to merge")
        return None
    
    # Use standardized output path if not specified
    if output_path is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = str(OUTPUT_DIR / f"educational_video_{timestamp}.mp4")
    
    try:
        # Create concat file for ffmpeg
        concat_file = str(TEMP_DIR / "concat_list.txt")
        with open(concat_file, "w", encoding='utf-8') as f:
            for segment in segments:
                video_path = segment.get("video_path")
                audio_path = segment.get("audio_path")
                
                if not video_path or not Path(video_path).exists():
                    print(f"✗ Video not found: {video_path}")
                    continue
                
                # If audio exists, add it to video
                if audio_path and Path(audio_path).exists():
                    # Create temp video with audio (don't use -shortest so video plays completely)
                    temp_video = str(TEMP_DIR / f"temp_segment_{segment.get('segment_id')}.mp4")
                    # Use -map to include both streams, video determines duration
                    cmd = f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v libx264 -c:a aac -b:a 192k -map 0:v:0 -map 1:a:0 "{temp_video}" -y -loglevel warning'
                    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                    if result.returncode == 0 and Path(temp_video).exists():
                        # Escape path for concat file: replace backslashes with forward slashes and escape special chars
                        safe_path = str(Path(temp_video).absolute()).replace('\\', '/')
                        f.write(f"file '{safe_path}'\n")
                        print(f"  ✓ Audio added to segment {segment.get('segment_id')}")
                    else:
                        print(f"  ✗ Audio merge failed for segment {segment.get('segment_id')}, using video only")
                        print(f"     Error: {result.stderr[:150]}")
                        # Fall back to video without audio
                        safe_path = str(Path(video_path).absolute()).replace('\\', '/')
                        f.write(f"file '{safe_path}'\n")
                else:
                    safe_path = str(Path(video_path).absolute()).replace('\\', '/')
                    f.write(f"file '{safe_path}'\n")
        
        # Concatenate all videos (re-encode to ensure compatibility)
        print("  Concatenating segments...")
        cmd = f'ffmpeg -f concat -safe 0 -i "{concat_file}" -c:v libx264 -c:a aac -b:a 192k "{output_path}" -y -loglevel warning'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        # Keep concat file for debugging, only delete if successful
        if result.returncode == 0:
            Path(concat_file).unlink()  # Clean up concat list
        else:
            print(f"  Concat file saved for debugging: {concat_file}")
        
        # Clean up temp videos
        import glob
        for temp_file in glob.glob(str(TEMP_DIR / "temp_segment_*.mp4")):
            Path(temp_file).unlink()
        
        if result.returncode == 0 and Path(output_path).exists():
            return output_path
        else:
            print(f"✗ ffmpeg concatenation error: {result.stderr[:200]}")
        return None
    except Exception as e:
        print(f"✗ Merge error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def generate_educational_video(topic: str):
    start_time = time.time()
    print(f"🎬 Starting pipeline for: {topic}\n")
    
    # Create output directories with standardized structure
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
    AUDIO_DIR.mkdir(exist_ok=True)
    VIDEO_DIR.mkdir(exist_ok=True)
    
    print(f"📁 Output directory: {OUTPUT_DIR}\n")
    
    # Get content plan
    print("📚 Creating lesson plan...")
    try:
        plan = await plan_lesson(qwen_client, topic)
    except Exception as e:
        print(f"✗ Failed to create lesson plan: {e}")
        return
    
    print(f"   Created {len(plan)} segments\n")
    
    segments_output = []
    video_paths = []
    
    # Generate intro slide
    print("  [INTRO] Title Slide... ", end="", flush=True)
    intro_prompt = f"""Generate a simple title slide for: \"{topic}\"
    - Show title centered with Text('{topic}', font_size=48).move_to(ORIGIN)
    - Add subtitle 'An Educational Video' below it
    - Use self.wait(3) to hold the slide
    - Keep it clean and professional with colors"""
    try:
        intro_code = await generate_code(qwen_client, intro_prompt)
        intro_code = re.sub(r"```python\n?|```\n?", "", intro_code).strip()
        intro_scene = extract_scene_name(intro_code)
        intro_result = execute_manim_code(intro_code, intro_scene, str(VIDEO_DIR))
        if intro_result["status"] == "success":
            print("✓")
            segments_output.append({
                "segment_id": "intro",
                "title": "Title Slide",
                "video_path": intro_result["video_path"],
                "audio_path": None,
                "status": "success"
            })
    except Exception as e:
        print(f"✗ {str(e)[:40]}")
    
    # Generate outline slide
    print("  [OUTLINE] Topics Overview... ", end="", flush=True)
    topics_list = "\\n".join([f"{i+1}. {seg['title']}" for i, seg in enumerate(plan)])
    outline_prompt = f"""Generate an outline slide showing:
    - Title: 'Topics We'll Cover Today' at top
    - Bullet list of topics:
{topics_list}
    - Use VGroup with Text objects positioned vertically
    - Use self.wait(4) to give time to read
    - Animate items appearing one by one with FadeIn"""
    try:
        outline_code = await generate_code(qwen_client, outline_prompt)
        outline_code = re.sub(r"```python\n?|```\n?", "", outline_code).strip()
        outline_scene = extract_scene_name(outline_code)
        outline_result = execute_manim_code(outline_code, outline_scene, str(VIDEO_DIR))
        if outline_result["status"] == "success":
            print("✓")
            segments_output.append({
                "segment_id": "outline",
                "title": "Outline",
                "video_path": outline_result["video_path"],
                "audio_path": None,
                "status": "success"
            })
    except Exception as e:
        print(f"✗ {str(e)[:40]}")
    
    print()
    
    for segment in plan:
        seg_id = segment.get("segment_id", "?")
        title = segment.get("title", "Untitled")
        concept = segment.get("concept", "")
        visual_type = segment.get("visual_type", "text")
        
        print(f"  [{seg_id}] {title}... ", end="", flush=True)
        
        # Retrieve image for scientific/complex concepts
        image_path = None
        if visual_type.lower() in ["diagram", "biology", "physics", "complex"] and SERPAPI_KEY:
            print("🖼️ ", end="", flush=True)
            image_result = get_image(concept, SERPAPI_KEY)
            if image_result['success']:
                image_path = image_result['path']
                print("✓ ", end="", flush=True)
            else:
                print("✗ ", end="", flush=True)
        
        # Get script for this segment
        script = segment.get("script", "")
        
        # Build prompt with script and image
        prompt = f"""Generate Manim scene for segment {seg_id}: {title}
Concept: {concept}
Visual type: {visual_type}

NARRATION SCRIPT (match visuals to this):
\"{script}\"

Create animations that DIRECTLY ILLUSTRATE what the narration describes.
Use SLOW animations and LONG waits (self.wait(3-4)) between sections.
Add pauses with self.wait(2) before transitions."""
        if image_path:
            prompt += f"\n\nInclude this educational image: ImageMobject('{image_path}').scale(1.5).to_edge(LEFT)"
        
        try:
            code = await generate_code(qwen_client, prompt)
        except Exception as e:
            print(f"✗ Code generation failed: {str(e)[:50]}")
            continue
        
        if not code:
            print("✗ Empty code returned")
            continue
        
        code = re.sub(r"```python\n?|```\n?", "", code).strip()
        scene_name = extract_scene_name(code)
        
        # Retry loop
        success = False
        for attempt in range(3):
            result = execute_manim_code(code, scene_name, str(VIDEO_DIR))
            if result["status"] == "success":
                print("✓", end="")
                
                # Generate audio for segment
                script = segment.get("script", "")
                if script:
                    print(" 🎤", end="", flush=True)
                    audio_path = str(AUDIO_DIR / f"segment_{seg_id}.mp3")
                    audio_result = generate_audio(script, audio_path)
                    if audio_result["success"]:
                        print(" ✓")
                    else:
                        print(f" ✗ (Audio: {audio_result['error'][:50]})")
                        audio_path = None
                else:
                    print()
                    audio_path = None
                
                segments_output.append({
                    "segment_id": seg_id,
                    "title": title,
                    "video_path": result["video_path"],
                    "audio_path": audio_path,
                    "status": "success"
                })
                video_paths.append(result["video_path"])
                success = True
                break
            
            if attempt < 2:
                try:
                    error_msg = result.get('error', 'Unknown error')
                    if error_msg:
                        code = await fix_code(qwen_client, code, error_msg[:300])
                        scene_name = extract_scene_name(code)
                    else:
                        print(" [No error message to fix]", end="")
                        break
                except Exception as e:
                    print(f" [Fix failed: {str(e)[:40]}]", end="")
                    break
        
        if not success:
            print("✗")
    
    # Save segment info
    segments_json = OUTPUT_DIR / "segments.json"
    with open(segments_json, "w") as f:
        json.dump(segments_output, f, indent=2)
    
    # Merge videos with audio
    print(f"\n🎥 Merging {len(segments_output)} segments with audio...")
    final_video = merge_videos(segments_output)
    
    if final_video:
        print(f"✓ Final video: {final_video}")
        # Optionally open the video
        # subprocess.Popen(["start", final_video], shell=True)
    else:
        print("✗ Failed to merge videos")
    
    elapsed = time.time() - start_time
    print(f"\n⏱️  Total execution time: {elapsed:.2f}s ({int(elapsed//60)}m {int(elapsed%60)}s)")

if __name__ == "__main__":
    asyncio.run(generate_educational_video("DNA structure and replication"))

