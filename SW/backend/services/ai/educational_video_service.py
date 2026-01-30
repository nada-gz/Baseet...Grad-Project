"""
Educational Video Generation Service
Handles video generation with fallback to config files and async job tracking.
"""
import asyncio
import uuid
import datetime
from pathlib import Path
from typing import Dict, Optional, Any
import sys

# Add educational-video-agent to path for imports
video_agent_path = Path(__file__).parent / "educational-video-agent"
if str(video_agent_path) not in sys.path:
    sys.path.insert(0, str(video_agent_path))

from pipeline_v2 import EducationalVideoPipeline


class VideoGenerationService:
    """Service for generating educational videos with async support."""
    
    def __init__(self):
        """Initialize the video generation service."""
        self.pipeline = EducationalVideoPipeline()
        self.async_jobs = {}  # job_id → job_status dict
        self.config_dir = Path(__file__).parent / "educational-video-agent"
    
    def _read_prompt_file(self) -> Optional[str]:
        """
        Read topic from prompt.txt file.
        
        Returns:
            Topic string or None if file doesn't exist or is empty
        """
        prompt_file = self.config_dir / "prompt.txt"
        
        if not prompt_file.exists():
            return None
        
        try:
            topic = prompt_file.read_text(encoding='utf-8').strip()
            return topic if topic else None
        except Exception:
            return None
    
    def _read_duration_file(self) -> float:
        """
        Read duration from duration.txt file.
        
        Returns:
            Duration in minutes (default: 1.0 if file doesn't exist or invalid)
        """
        duration_file = self.config_dir / "duration.txt"
        
        if not duration_file.exists():
            return 1.0
        
        try:
            duration_text = duration_file.read_text(encoding='utf-8').strip()
            duration = float(duration_text)
            
            # Validate duration
            if duration <= 0 or duration > 10:
                return 1.0
            
            return duration
        except Exception:
            return 1.0
    
    def get_video_parameters(self, topic: Optional[str], duration: Optional[float]) -> tuple:
        """
        Get video parameters with fallback to config files.
        
        Args:
            topic: User-provided topic (optional)
            duration: User-provided duration in minutes (optional)
            
        Returns:
            (topic, duration) tuple
            
        Raises:
            ValueError: If topic is empty after fallback
        """
        # Fallback to prompt.txt if topic not provided
        if not topic or not topic.strip():
            topic = self._read_prompt_file()
        else:
            topic = topic.strip()
        
        # Fallback to duration.txt if duration not provided
        if duration is None:
            duration = self._read_duration_file()
        else:
            # Validate user-provided duration
            try:
                duration = float(duration)
                if duration <= 0 or duration > 10:
                    duration = self._read_duration_file()
            except (ValueError, TypeError):
                duration = self._read_duration_file()
        
        # Final validation
        if not topic:
            raise ValueError("No topic provided and prompt.txt is empty or missing")
        
        return topic, duration
    
    async def generate_video_sync(self, topic: Optional[str], duration: Optional[float]) -> Dict[str, Any]:
        """
        Generate video synchronously.
        
        Args:
            topic: Video topic (optional, falls back to prompt.txt)
            duration: Video duration in minutes (optional, falls back to duration.txt)
            
        Returns:
            Dict with:
                - success: bool
                - video_path: str (only final video path)
                - video_url: str (downloadable URL)
                - session_id: str
                - message: str
                - generation_time_seconds: float
                - error: Optional[str]
        """
        try:
            # Get parameters with fallback
            topic, duration = self.get_video_parameters(topic, duration)
            
            # Create a temporary pipeline with trace callback
            pipeline = EducationalVideoPipeline(
                trace_callback=None,  # Silent for API
                target_duration_minutes=duration
            )
            
            # Generate the video
            result = await pipeline.generate(topic)
            
            # Extract only the final video path from outputs
            if result.get("success") and result.get("video_path"):
                video_path = result.get("video_path")
                session_id = result.get("session_dir", "").split("\\")[-1] if result.get("session_dir") else "unknown"
                
                return {
                    "success": True,
                    "video_path": str(video_path),
                    "video_url": f"/ai/video/download/{session_id}",
                    "session_id": session_id,
                    "message": "Video generated successfully",
                    "generation_time_seconds": result.get("generation_time", 0),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "video_path": None,
                    "video_url": None,
                    "session_id": None,
                    "message": "Video generation failed",
                    "generation_time_seconds": None,
                    "error": result.get("error", "Unknown error")
                }
                
        except ValueError as e:
            return {
                "success": False,
                "video_path": None,
                "video_url": None,
                "session_id": None,
                "message": "Invalid input parameters",
                "generation_time_seconds": None,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "video_path": None,
                "video_url": None,
                "session_id": None,
                "message": "Video generation error",
                "generation_time_seconds": None,
                "error": str(e)
            }
    
    async def generate_video_async(self, topic: Optional[str], duration: Optional[float]) -> Dict[str, Any]:
        """
        Generate video asynchronously and return job_id for polling.
        
        Args:
            topic: Video topic (optional)
            duration: Video duration in minutes (optional)
            
        Returns:
            Dict with:
                - success: bool
                - job_id: str (unique job identifier)
                - status: str ("queued")
                - message: str
                - poll_url: str
        """
        try:
            # Validate parameters early
            topic, duration = self.get_video_parameters(topic, duration)
            
            # Generate unique job ID
            job_id = str(uuid.uuid4())[:8]
            
            # Create job entry
            self.async_jobs[job_id] = {
                "status": "queued",
                "topic": topic,
                "duration": duration,
                "progress": 0,
                "started_at": datetime.datetime.now().isoformat(),
                "video_path": None,
                "error": None
            }
            
            # Queue background task
            asyncio.create_task(self._process_video_job(job_id, topic, duration))
            
            return {
                "success": True,
                "job_id": job_id,
                "status": "queued",
                "message": f"Video generation queued. Job ID: {job_id}",
                "poll_url": f"/ai/video/status/{job_id}"
            }
            
        except ValueError as e:
            return {
                "success": False,
                "job_id": None,
                "status": "error",
                "message": "Invalid parameters",
                "poll_url": None,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "job_id": None,
                "status": "error",
                "message": "Job creation failed",
                "poll_url": None,
                "error": str(e)
            }
    
    async def _process_video_job(self, job_id: str, topic: str, duration: float):
        """
        Background task to process video generation.
        
        Args:
            job_id: Unique job identifier
            topic: Video topic
            duration: Video duration in minutes
        """
        try:
            self.async_jobs[job_id]["status"] = "processing"
            self.async_jobs[job_id]["progress"] = 10
            
            # Generate video
            pipeline = EducationalVideoPipeline(
                trace_callback=None,
                target_duration_minutes=duration
            )
            
            result = await pipeline.generate(topic)
            
            self.async_jobs[job_id]["progress"] = 100
            
            if result.get("success"):
                self.async_jobs[job_id].update({
                    "status": "completed",
                    "video_path": result.get("video_path"),
                    "session_id": result.get("session_dir", "").split("\\")[-1] if result.get("session_dir") else "unknown",
                    "completed_at": datetime.datetime.now().isoformat(),
                    "error": None
                })
            else:
                self.async_jobs[job_id].update({
                    "status": "failed",
                    "error": result.get("error", "Unknown error"),
                    "completed_at": datetime.datetime.now().isoformat()
                })
                
        except Exception as e:
            self.async_jobs[job_id].update({
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.datetime.now().isoformat()
            })
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get status of async video generation job.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Dict with job status information
            
        Raises:
            ValueError: If job_id not found
        """
        if job_id not in self.async_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.async_jobs[job_id]
        
        return {
            "job_id": job_id,
            "status": job["status"],
            "progress": job.get("progress", 0),
            "topic": job.get("topic"),
            "duration": job.get("duration"),
            "video_path": job.get("video_path"),
            "session_id": job.get("session_id"),
            "error": job.get("error"),
            "started_at": job.get("started_at"),
            "completed_at": job.get("completed_at")
        }
    
    def get_video_file_path(self, session_id: str) -> Optional[Path]:
        """
        Get the actual file path for a generated video.
        
        Args:
            session_id: Session ID of the generated video
            
        Returns:
            Path object to video file or None if not found
        """
        # Search in outputs/final/{session_id}/
        base_output_dir = self.config_dir / "outputs" / "final" / session_id
        
        if not base_output_dir.exists():
            return None
        
        # Look for final_*.mp4 files
        for video_file in base_output_dir.glob("final_*.mp4"):
            return video_file
        
        return None
    
    def list_generated_videos(self, limit: int = 10) -> list:
        """
        List recently generated videos.
        
        Args:
            limit: Maximum number of videos to return
            
        Returns:
            List of video info dicts
        """
        videos = []
        output_dir = self.config_dir / "outputs" / "final"
        
        if not output_dir.exists():
            return videos
        
        # Get all session directories, sorted by modification time (newest first)
        session_dirs = sorted(
            [d for d in output_dir.iterdir() if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:limit]
        
        for session_dir in session_dirs:
            # Look for video file
            video_file = None
            for vf in session_dir.glob("final_*.mp4"):
                video_file = vf
                break
            
            if video_file:
                videos.append({
                    "session_id": session_dir.name,
                    "video_path": str(video_file),
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
