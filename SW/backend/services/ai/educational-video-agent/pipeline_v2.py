"""
Clean Educational Video Pipeline
- English visuals with Arabic narration
- Single output directory
- Clear tracing and logging
"""
import asyncio
import json
import re
import time
import uuid
from pathlib import Path
from typing import Callable, Optional, List, Dict, Any
from dataclasses import dataclass, field

from config import (
    init_output_dirs, get_session_dir, cleanup_temp,
    VIDEO_OUTPUT_DIR, AUDIO_OUTPUT_DIR
)
from llm import QwenClient, plan_lesson, generate_code, fix_code
from tools.manim_executor import execute_manim_code
from tools.enhanced_arabic_tts import generate_arabic_narration_async  # ElevenLabs + Edge-TTS fallback
from tools.image_processor import search_and_download_image
from tools.video_merger import merge_video_segments
from tools.code_validator import validate_manim_code, get_validation_summary


@dataclass
class PipelineTrace:
    """Tracks all operations for debugging and UI display."""
    logs: List[str] = field(default_factory=list)
    api_calls: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    segments: List[Dict] = field(default_factory=list)
    
    def log(self, msg: str):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {msg}"
        self.logs.append(entry)
        print(entry)
    
    def api_call(self, name: str, input_preview: str, output_preview: str):
        self.api_calls.append({
            "time": time.strftime("%H:%M:%S"),
            "name": name,
            "input": input_preview[:100],
            "output": output_preview[:200]
        })
    
    def error(self, msg: str):
        self.errors.append(msg)
        self.log(f"❌ ERROR: {msg}")
    
    def to_dict(self) -> Dict:
        return {
            "logs": self.logs,
            "api_calls": self.api_calls,
            "errors": self.errors,
            "segments": self.segments
        }


class EducationalVideoPipeline:
    """
    Generates educational videos with:
    - English visuals (Manim)
    - Arabic audio narration
    - Clean single output directory
    - Configurable target duration
    """
    
    def __init__(self, trace_callback: Callable[[str], None] = None, 
                 target_duration_minutes: float = 1.0):
        """
        Args:
            trace_callback: Optional callback called with log messages
            target_duration_minutes: Target video duration in minutes (default: 1 minute)
        """
        self.trace = PipelineTrace()
        self.trace_callback = trace_callback
        self.qwen_client = None
        self.session_id = None
        self.session_dir = None
        self.target_duration = target_duration_minutes  # in minutes
        
    def _log(self, msg: str):
        """Log message to trace and callback."""
        self.trace.log(msg)
        if self.trace_callback:
            self.trace_callback(msg)
    
    def _init_session(self) -> Path:
        """Initialize a new pipeline session with clean output structure."""
        self.session_id = time.strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:4]
        init_output_dirs()
        self.session_dir = get_session_dir(self.session_id)
        self._log(f"📁 Session: {self.session_id}")
        self._log(f"📁 Output: {self.session_dir}")
        self._log(f"🎯 Target duration: {self.target_duration} minute(s)")
        return self.session_dir
    
    def _cleanup_manim_temp(self):
        """Clean up temporary Manim folders (Tex, images, partial files)."""
        import shutil
        try:
            videos_dir = self.session_dir / "videos"
            if videos_dir.exists():
                # Remove Tex, images, texts folders
                for folder in ["Tex", "images", "texts"]:
                    folder_path = videos_dir / folder
                    if folder_path.exists():
                        shutil.rmtree(folder_path, ignore_errors=True)
                
                # Remove temp video folders (tmp*)
                videos_subdir = videos_dir / "videos"
                if videos_subdir.exists():
                    for item in videos_subdir.iterdir():
                        if item.is_dir() and item.name.startswith("tmp"):
                            shutil.rmtree(item, ignore_errors=True)
            
            # Also clean the temp directory
            temp_dir = self.session_dir / "temp"
            if temp_dir.exists():
                for item in temp_dir.iterdir():
                    if item.name.startswith("scaled_"):
                        item.unlink()
            
            self._log("🧹 Cleaned up temp files")
        except Exception as e:
            self._log(f"⚠️ Cleanup warning: {e}")
    
    async def _create_lesson_plan(self, topic: str) -> List[Dict]:
        """Generate lesson plan with Arabic scripts."""
        self._log(f"📚 Creating lesson plan (target: {self.target_duration} min)...")
        
        if not self.qwen_client:
            self.qwen_client = QwenClient()
        
        plan = await plan_lesson(self.qwen_client, topic, self.target_duration)
        
        self.trace.api_call(
            "plan_lesson",
            f"Topic: {topic}",
            f"Created {len(plan)} segments"
        )
        
        # Add Arabic narration scripts to each segment
        self._log("🌍 Generating Arabic narration scripts...")
        
        for seg in plan:
            english_script = seg.get("script", seg.get("concept", ""))
            
            # Generate Arabic translation - simple and clear
            arabic_prompt = f"""Translate this educational narration to simple, clear Modern Standard Arabic (العربية الفصحى المبسطة).

Keep it:
- Simple and easy to understand
- Clear and professional
- Suitable for students
- Use simple vocabulary, avoid complex or archaic words

English: {english_script}

Respond with ONLY the Arabic text, nothing else."""
            
            try:
                arabic_script = await self.qwen_client.call(
                    system_prompt="You are a translator. Translate to simple, clear Modern Standard Arabic for educational content.",
                    user_prompt=arabic_prompt,
                    temperature=0.3
                )
                seg["arabic_script"] = arabic_script.strip()
                self._log(f"  ✅ Segment {seg.get('segment_id')}: Arabic script ready")
            except Exception as e:
                seg["arabic_script"] = ""
                self._log(f"  ⚠️ Segment {seg.get('segment_id')}: Arabic translation failed")
        
        self._log(f"📋 Plan ready: {len(plan)} segments")
        return plan
    
    def _extract_scene_name(self, code: str) -> str:
        """Extract Manim scene class name from code."""
        match = re.search(r'class\s+(\w+)\s*\(\s*Scene\s*\)', code)
        return match.group(1) if match else "Scene"
    
    async def _generate_segment_video(self, segment: Dict, index: int) -> Dict:
        """Generate video for a single segment."""
        seg_id = segment.get("segment_id", index)
        title = segment.get("title", "Untitled")
        concept = segment.get("concept", "")
        visual_type = segment.get("visual_type", "text")
        english_script = segment.get("script", "")
        
        self._log(f"🎬 Segment {seg_id}: {title}")
        
        result = {
            "segment_id": seg_id,
            "title": title,
            "video_path": None,
            "audio_path": None,
            "status": "pending"
        }
        
        # Search for image if needed
        image_path = None
        if visual_type.lower() in ["diagram", "biology", "physics", "complex", "image"]:
            self._log(f"  🖼️ Searching for image: {concept[:40]}...")
            img_result = search_and_download_image(concept, self.session_dir)
            if img_result["success"]:
                image_path = img_result["path"]
                self._log(f"  ✅ Image found" + (" (cached)" if img_result.get("cached") else ""))
            else:
                self._log(f"  ⚠️ No image found")
        
        # Generate Manim code
        prompt = f"""Generate a Manim scene for: {title}
Concept: {concept}
Visual type: {visual_type}

The narration says: "{english_script}"

**CRITICAL - NO BLACK SCREENS**:
- ALWAYS have something visible on screen
- When transitioning, fade out old content WHILE fading in new content
- Use overlapping animations: self.play(FadeOut(old), FadeIn(new))
- Keep a title or background text visible during transitions
- NO empty self.wait() with black screen

Requirements:
- **PREFER SIMPLE VISUALS**: Use text labels and basic shapes
- For science topics: Let the IMAGE be the main visual, add only simple text labels
- Use self.wait(2-3) between major elements
- Match visuals to what the narration describes
- Keep text in English, clean and readable
- Use colors to highlight important elements"""

        if image_path:
            # Use forward slashes for Manim
            safe_image_path = str(Path(image_path).absolute()).replace("\\", "/")
            prompt += f"""

**IMPORTANT - IMAGE PROVIDED**:
- This is a SCIENCE topic with a real image - use it as the PRIMARY visual
- Include: ImageMobject("{safe_image_path}").scale_to_fit_width(5.5)
- **IMAGE SIZE**: Keep width between 5-7 (not too small, not too large)
- Position the image prominently (center or slightly to one side)
- Add ONLY simple text labels pointing to parts of the image
- DO NOT create complex animations - the image explains the concept
- Keep it simple: Show image → Add 1-2 text labels → Done
- Keep the image visible for most of the segment duration"""
        
        try:
            code = await generate_code(self.qwen_client, prompt)
            code = re.sub(r"```python\n?|```\n?", "", code).strip()
            
            self.trace.api_call("generate_code", prompt[:100], code[:200])
            
            # Validate code before rendering
            validation = validate_manim_code(code)
            self._log(f"  {get_validation_summary(validation)}")
            
            # If there are critical errors, try to fix them immediately
            if not validation['valid']:
                self._log(f"  🔧 Pre-fixing validation errors...")
                error_msg = "; ".join(validation['errors'])
                try:
                    code = await fix_code(self.qwen_client, code, error_msg)
                    code = re.sub(r"```python\n?|```\n?", "", code).strip()
                    # Re-validate
                    validation = validate_manim_code(code)
                    self._log(f"  {get_validation_summary(validation)}")
                except Exception as fix_err:
                    self._log(f"  ⚠️  Pre-fix failed: {fix_err}")
            
        except Exception as e:
            self._log(f"  ❌ Code generation failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
            return result
        
        # Execute Manim with retries
        scene_name = self._extract_scene_name(code)
        video_dir = str(self.session_dir / "videos")
        
        for attempt in range(3):
            self._log(f"  🎥 Rendering (attempt {attempt + 1}/3)...")
            
            manim_result = execute_manim_code(code, scene_name, video_dir)
            
            if manim_result["status"] == "success":
                result["video_path"] = manim_result["video_path"]
                self._log(f"  ✅ Video rendered")
                break
            else:
                error = manim_result.get("error", "Unknown error")
                self._log(f"  ⚠️ Render failed: {error[:80]}")
                
                # Save full error and code for debugging
                if attempt == 0:  # Only save on first attempt to avoid clutter
                    debug_dir = self.session_dir / "debug"
                    debug_dir.mkdir(exist_ok=True)
                    
                    # Save the generated code
                    code_file = debug_dir / f"segment_{seg_id}_attempt_{attempt + 1}_code.py"
                    with open(code_file, "w", encoding="utf-8") as f:
                        f.write(code)
                    
                    # Save the full error message
                    error_file = debug_dir / f"segment_{seg_id}_attempt_{attempt + 1}_error.txt"
                    with open(error_file, "w", encoding="utf-8") as f:
                        f.write(f"Segment: {title}\n")
                        f.write(f"Scene Name: {scene_name}\n")
                        f.write(f"Attempt: {attempt + 1}\n")
                        f.write(f"\n{'=' * 70}\n")
                        f.write(f"FULL ERROR MESSAGE:\n")
                        f.write(f"{'=' * 70}\n")
                        f.write(error)
                    
                    self._log(f"  📝 Debug files saved to: {debug_dir}")
                
                if attempt < 2:
                    self._log(f"  🔧 Attempting fix...")
                    try:
                        code = await fix_code(self.qwen_client, code, error[:1500])  # Increased from 300
                        code = re.sub(r"```python\n?|```\n?", "", code).strip()
                        scene_name = self._extract_scene_name(code)
                    except:
                        pass
        
        if not result["video_path"]:
            result["status"] = "failed"
            result["error"] = "Video rendering failed after 3 attempts"
            return result
        
        # Generate Arabic audio
        arabic_script = segment.get("arabic_script", "")
        if arabic_script:
            self._log(f"  🎤 Generating Arabic narration...")
            audio_path = str(self.session_dir / "audio" / f"segment_{seg_id}.mp3")
            
            audio_result = await generate_arabic_narration_async(arabic_script, audio_path)
            
            if audio_result["success"]:
                result["audio_path"] = audio_result["audio_path"]
                self._log(f"  ✅ Audio generated")
            else:
                self._log(f"  ⚠️ Audio failed: {audio_result.get('error', 'Unknown')[:50]}")
        
        result["status"] = "success"
        return result
    
    async def _generate_intro_slide(self, topic: str) -> Optional[Dict]:
        """Generate title slide."""
        self._log("🎬 Generating intro slide...")
        
        prompt = f"""Generate a simple Manim title slide for: "{topic}"
- Center the title using Text('{topic}', font_size=48).move_to(ORIGIN)
- Add subtitle 'An Educational Video' below
- Use FadeIn animations
- Use self.wait(3) to hold the slide
- Keep it clean and professional"""
        
        try:
            code = await generate_code(self.qwen_client, prompt)
            code = re.sub(r"```python\n?|```\n?", "", code).strip()
            scene_name = self._extract_scene_name(code)
            
            video_dir = str(self.session_dir / "videos")
            result = execute_manim_code(code, scene_name, video_dir)
            
            if result["status"] == "success":
                self._log("  ✅ Intro slide ready")
                return {
                    "segment_id": "intro",
                    "title": "Introduction",
                    "video_path": result["video_path"],
                    "audio_path": None,
                    "status": "success"
                }
        except Exception as e:
            self._log(f"  ⚠️ Intro generation failed: {e}")
        
        return None
    
    async def generate(self, topic: str) -> Dict[str, Any]:
        """
        Main entry point - generate educational video.
        
        Args:
            topic: The educational topic to create video about
            
        Returns:
            Dict with:
                - success: bool
                - video_path: path to final video (or None)
                - session_dir: path to all outputs
                - trace: full trace data
        """
        start_time = time.time()
        
        self._log("=" * 50)
        self._log(f"🎬 Educational Video Generator")
        self._log(f"📝 Topic: {topic}")
        self._log("=" * 50)
        
        # Initialize session
        self._init_session()
        
        try:
            # Create lesson plan with Arabic scripts
            plan = await self._create_lesson_plan(topic)
            
            if not plan:
                self._log("❌ Failed to create lesson plan")
                return {
                    "success": False,
                    "video_path": None,
                    "session_dir": str(self.session_dir),
                    "trace": self.trace.to_dict()
                }
            
            # Generate all segments
            segments = []
            
            # Intro slide
            intro = await self._generate_intro_slide(topic)
            if intro:
                segments.append(intro)
            
            # Content segments
            for i, seg in enumerate(plan):
                seg_result = await self._generate_segment_video(seg, i + 1)
                segments.append(seg_result)
                self.trace.segments.append(seg_result)
            
            # Filter successful segments
            valid_segments = [s for s in segments if s.get("video_path")]
            
            if not valid_segments:
                self._log("❌ No valid video segments generated")
                return {
                    "success": False,
                    "video_path": None,
                    "session_dir": str(self.session_dir),
                    "trace": self.trace.to_dict()
                }
            
            # Merge all segments
            self._log(f"\n🔀 Merging {len(valid_segments)} segments...")
            
            final_path = str(self.session_dir / f"final_{topic.replace(' ', '_')[:30]}.mp4")
            
            merged_video = merge_video_segments(
                valid_segments, 
                output_path=final_path,
                session_dir=self.session_dir,
                trace_callback=self._log
            )
            
            # Save metadata
            metadata = {
                "topic": topic,
                "session_id": self.session_id,
                "target_duration_minutes": self.target_duration,
                "segments": segments,
                "final_video": merged_video,
                "generation_time_seconds": time.time() - start_time
            }
            
            metadata_path = self.session_dir / "metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Cleanup temp Manim folders
            self._cleanup_manim_temp()
            
            elapsed = time.time() - start_time
            self._log(f"\n⏱️ Total time: {int(elapsed // 60)}m {int(elapsed % 60)}s")
            
            if merged_video:
                self._log(f"✅ SUCCESS: {merged_video}")
            else:
                self._log("⚠️ Video merge failed - check individual segments")
            
            return {
                "success": merged_video is not None,
                "video_path": merged_video,
                "session_dir": str(self.session_dir),
                "trace": self.trace.to_dict()
            }
            
        except Exception as e:
            import traceback
            self.trace.error(f"Pipeline error: {str(e)}")
            self._log(traceback.format_exc())
            
            return {
                "success": False,
                "video_path": None,
                "session_dir": str(self.session_dir) if self.session_dir else None,
                "trace": self.trace.to_dict(),
                "error": str(e)
            }


async def generate_video(topic: str, trace_callback: Callable[[str], None] = None,
                        target_duration_minutes: float = 1.0) -> Dict:
    """
    Convenience function to generate a video.
    
    Args:
        topic: Educational topic
        trace_callback: Optional callback for progress updates
        target_duration_minutes: Target video duration (default: 1 minute)
        
    Returns:
        Result dict with success, video_path, session_dir, trace
    """
    pipeline = EducationalVideoPipeline(
        trace_callback=trace_callback,
        target_duration_minutes=target_duration_minutes
    )
    return await pipeline.generate(topic)


if __name__ == "__main__":
    # Test run
    import sys
    
    topic = sys.argv[1] if len(sys.argv) > 1 else "Newton's Laws of Motion"
    duration = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0  # Default 1 minute
    
    print(f"Generating video about '{topic}' (target: {duration} minute(s))")
    
    result = asyncio.run(generate_video(topic, target_duration_minutes=duration))
    
    print("\n" + "=" * 50)
    print("RESULT:")
    print(f"  Success: {result['success']}")
    print(f"  Video: {result.get('video_path')}")
    print(f"  Session: {result.get('session_dir')}")
    if result.get('error'):
        print(f"  Error: {result['error']}")
