"""
Educational Video Generation Service - Integrated with the new React/Remotion-based Egyptian Arabic Kids Explainer pipeline.
"""
import asyncio
import os
import sys
import uuid
import time
import datetime
from pathlib import Path
from typing import Dict, Optional, Any

# Root of the AI video project
AI_VIDEO_DIR = Path(__file__).parent / "video"

class VideoGenerationService:
    """Service for generating educational videos using the new Kids Explainer pipeline."""
    
    def __init__(self):
        """Initialize the video generation service."""
        # Config folder mapping to the new pipeline directory
        self.config_dir = AI_VIDEO_DIR
        self.projects_dir = AI_VIDEO_DIR / "projects"
        self.async_jobs = {}
        
    def _read_prompt_file(self) -> Optional[str]:
        """Read fallback topic prompt."""
        # Simple static mock to satisfy health check API
        return "النباتات كائنات حية"

    def _read_duration_file(self) -> float:
        """Read fallback duration."""
        return 1.0

    def get_video_parameters(self, topic: Optional[str], duration: Optional[float]) -> tuple:
        """Get video parameters with fallbacks."""
        if not topic or not topic.strip():
            topic = self._read_prompt_file()
        if duration is None:
            duration = self._read_duration_file()
        return topic, duration

    async def generate_video_sync(self, topic: Optional[str], duration: Optional[float],
                               lesson_id: Optional[int] = None, student_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate video synchronously by running the kids-explainer pipeline.
        
        Args:
            topic: Video topic text (Ammiya Arabic explanation)
            duration: Video duration in minutes (not directly mapped, but kept for interface compatibility)
            lesson_id: Associated lesson ID
            student_id: Associated student ID
            
        Returns:
            Dict matching VideoResponse schema
        """
        t0 = time.time()
        
        # 1. Standardize parameters
        topic, duration = self.get_video_parameters(topic, duration)
        
        # 2. Generate a unique session ID
        session_id = f"video_std_{student_id}_les_{lesson_id}_{uuid.uuid4().hex[:6]}"
        session_dir = self.projects_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # 3. Write topic text to a temporary file in the session dir
        topic_file = session_dir / "topic.txt"
        topic_file.write_text(topic, encoding="utf-8")
        
        # 4. Invoke the subprocess running the pipeline script
        # Resolve the venv Python that is running this service (same env = same deps)
        python_exe = sys.executable or "python3"
        pipeline_script = AI_VIDEO_DIR / "run_pipeline.py"
        
        # Build subprocess environment: inherit current env + inject GEMINI_API_KEY
        # so run_pipeline.py can always find it even if it can't find the .env file.
        sub_env = os.environ.copy()
        # Forward any keys that might not be in the subprocess environment
        for key in ("GEMINI_API_KEY", "GROQ_API_KEY", "PIXABAY_API_KEY", "HF_TOKEN", "ELEVENLABS_API_KEY"):
            val = os.environ.get(key)
            if val:
                sub_env[key] = val

        print(f"🎬 [Service] Starting video generation job for session {session_id}...", flush=True)
        print(f"   python: {python_exe}", flush=True)
        
        try:
            # cwd must be AI_VIDEO_DIR so relative paths inside run_pipeline.py resolve correctly
            proc = await asyncio.create_subprocess_exec(
                python_exe,
                str(pipeline_script),
                "--file", str(topic_file),
                "--session", session_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,   # merge stderr into stdout for full log
                cwd=str(AI_VIDEO_DIR),
                env=sub_env,
            )
            
            # Wait for execution to finish
            stdout, _ = await proc.communicate()
            
            # Check success
            final_video_path = session_dir / "renders" / "final.mp4"
            
            # 5. Clean up the temporary topic file
            try:
                topic_file.unlink()
            except Exception:
                pass
                
            if proc.returncode == 0 and final_video_path.exists():
                elapsed = time.time() - t0
                print(f"✅ [Service] Video generated successfully in {elapsed:.1f}s at: {final_video_path}", flush=True)
                
                return {
                    "success": True,
                    "video_path": str(final_video_path),
                    "video_url": f"/ai/video/download/{session_id}",
                    "session_id": session_id,
                    "message": "Video generated successfully",
                    "generation_time_seconds": elapsed,
                    "error": None
                }
            else:
                err_msg = stdout.decode(errors="replace").strip() if stdout else ""
                print(f"❌ [Service] Pipeline execution failed (code {proc.returncode}): {err_msg}", flush=True)
                return {
                    "success": False,
                    "video_path": None,
                    "video_url": None,
                    "session_id": None,
                    "message": "Video generation failed in pipeline",
                    "generation_time_seconds": None,
                    "error": err_msg or f"Process exited with code {proc.returncode}"
                }
                
        except Exception as e:
            print(f"❌ [Service] Subprocess execution error: {e}", flush=True)
            return {
                "success": False,
                "video_path": None,
                "video_url": None,
                "session_id": None,
                "message": "Subprocess execution error",
                "generation_time_seconds": None,
                "error": str(e)
            }

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Legacy compatibility helper."""
        return {"status": "unknown"}

    def get_video_file_path(self, session_id: str) -> Optional[Path]:
        """
        Get the actual file path for a generated video.
        
        Args:
            session_id: Session ID of the generated video
            
        Returns:
            Path object to video file or None if not found
        """
        final_video_path = self.projects_dir / session_id / "renders" / "final.mp4"
        if final_video_path.exists():
            return final_video_path
        return None

    def list_generated_videos(self, limit: int = 10) -> list:
        """List recently generated videos."""
        videos = []
        if not self.projects_dir.exists():
            return videos
            
        # Get all subdirectories in projects, sorted by modification time
        session_dirs = sorted(
            [d for d in self.projects_dir.iterdir() if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:limit]
        
        for session_dir in session_dirs:
            vf = session_dir / "renders" / "final.mp4"
            if vf.exists():
                videos.append({
                    "session_id": session_dir.name,
                    "video_path": str(vf),
                    "created_at": datetime.datetime.fromtimestamp(session_dir.stat().st_mtime).isoformat(),
                    "video_url": f"/ai/video/download/{session_dir.name}"
                })
        return videos

# Singleton instance
_service_instance = None

def get_video_service() -> VideoGenerationService:
    """Get or create video generation service singleton."""
    global _service_instance
    if _service_instance is None:
        _service_instance = VideoGenerationService()
    return _service_instance
