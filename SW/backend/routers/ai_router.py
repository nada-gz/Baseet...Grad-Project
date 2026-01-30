from fastapi import APIRouter, HTTPException, FileResponse
from pydantic import BaseModel
from typing import Optional
import datetime
from pathlib import Path

from services.ai.ai_service import (
    sessions,
    fetch_lesson_by_id,
    orchestrator,
    process_text_input,
    process_voice_input,
    speak_text
)
from services.ai.educational_video_service import get_video_service

router = APIRouter(prefix="/ai", tags=["AI"])

# =========================
# Pydantic Models
# =========================
class StartLessonRequest(BaseModel):
    lesson_id: int
    student_id: int


class ChatRequest(BaseModel):
    lesson_id: int
    student_id: int
    message: str = ""


class BotResponse(BaseModel):
    message: str
    state: str
    progress: Optional[int] = 0


# =========================
# VIDEO GENERATION MODELS
# =========================
class GenerateVideoRequest(BaseModel):
    """Request model for video generation."""
    topic: Optional[str] = None          # User's video topic (optional, falls back to prompt.txt)
    duration: Optional[float] = None     # Duration in minutes (optional, falls back to duration.txt)
    student_id: Optional[int] = None     # Student ID for tracking (optional)
    session_id: Optional[str] = None     # Custom session ID (optional)


class GenerateVideoResponse(BaseModel):
    """Response model for video generation."""
    success: bool
    video_path: Optional[str] = None     # Local path to final video
    video_url: Optional[str] = None      # HTTP URL to download video
    session_id: Optional[str] = None     # Session ID for reference
    message: str
    generation_time_seconds: Optional[float] = None
    error: Optional[str] = None


class GenerateVideoAsyncRequest(BaseModel):
    """Request model for asynchronous video generation."""
    topic: Optional[str] = None
    duration: Optional[float] = None
    student_id: Optional[int] = None
    session_id: Optional[str] = None


class GenerateVideoAsyncResponse(BaseModel):
    """Response model for async video generation."""
    success: bool
    job_id: Optional[str] = None
    status: str
    message: str
    poll_url: Optional[str] = None
    error: Optional[str] = None


class VideoStatusResponse(BaseModel):
    """Response model for video job status."""
    job_id: str
    status: str  # "queued", "processing", "completed", "failed"
    progress: Optional[int] = None
    topic: Optional[str] = None
    duration: Optional[float] = None
    video_path: Optional[str] = None
    session_id: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class VideoListResponse(BaseModel):
    """Response model for listing videos."""
    success: bool
    videos: list
    count: int
    message: str


# =========================
# START LESSON (Updated to use Orchestrator)
# =========================
@router.post("/lesson/start", response_model=BotResponse)
async def start_lesson(request: StartLessonRequest):
    student_id = str(request.student_id)
    session_id = f"student_{student_id}_lesson_{request.lesson_id}"

    # Call the smart orchestrator with NO input to start the lesson
    result = orchestrator.run_interactive_lesson(
        lesson_id=request.lesson_id,
        session_id=session_id,
        user_input=None,  # None signals "Start this lesson"
        use_tts=False,    # Disable TTS for this chat endpoint (optional)
        use_stt=False
    )

    return BotResponse(
        message=result.get("message", "Error starting lesson"),
        state=result.get("state", "error"),
        progress=result.get("progress", 0)
    )


# =========================
# AI CHAT (Updated to use Orchestrator)
# =========================
@router.post("/lesson/chat", response_model=BotResponse)
async def chat_lesson(request: ChatRequest):
    student_id = str(request.student_id)
    session_id = f"student_{student_id}_lesson_{request.lesson_id}"
    user_input = request.message.strip()

    # Call the smart orchestrator with the user's message
    result = orchestrator.run_interactive_lesson(
        lesson_id=request.lesson_id,
        session_id=session_id,
        user_input=user_input,
        use_tts=False, # Usually chat interfaces don't auto-play audio
        use_stt=False
    )

    return BotResponse(
        message=result.get("message", "Error processing request"),
        state=result.get("state", "error"),
        progress=result.get("progress", 0)
    )


# =========================
# STT & TTS ENDPOINTS
# =========================

class VoiceInputRequest(BaseModel):
    """Request model for voice input (STT)."""
    session_id: Optional[str] = "default"


class TTSRequest(BaseModel):
    """Request model for text-to-speech."""
    text: str


class TextInputRequest(BaseModel):
    """Request model for SmartOrchestrator text input."""
    text: str
    session_id: Optional[str] = "default"


@router.post("/voice")
async def process_voice_endpoint(request: VoiceInputRequest):
    """Process voice input using STT module."""
    try:
        result = process_voice_input(request.session_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Voice processing failed")
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")


@router.post("/speak")
async def text_to_speech_endpoint(request: TTSRequest):
    """Convert text to speech using TTS module."""
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required for TTS")
    
    try:
        result = speak_text(request.text)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "TTS failed")
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


@router.post("/orchestrator/process")
async def smart_orchestrator_endpoint(request: TextInputRequest):
    """Process text input through SmartOrchestrator."""
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text input is required")
    
    try:
        result = process_text_input(request.text, request.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.get("/orchestrator/health")
async def orchestrator_health():
    """Health check for SmartOrchestrator modules."""
    return {
        "status": "healthy",
        "modules": {
            "cutter": orchestrator is not None,
            "explanation": True,
            "tts": orchestrator.voice is not None if orchestrator else False,
            "stt": orchestrator.ear is not None if orchestrator else False
        }
    }


# =========================
# INTERACTIVE LESSON (UNIFIED LOOP)
# =========================

class InteractiveLessonRequest(BaseModel):
    """Request model for starting/continuing an interactive lesson."""
    lesson_id: int
    student_id: int
    user_input: Optional[str] = None
    enable_tts: bool = True 
    enable_stt: bool = True


class InteractiveLessonResponse(BaseModel):
    """Response model for interactive lesson state."""
    success: bool
    state: str
    message: str
    audio_played: bool = False
    prompt: Optional[str] = None
    is_correct: Optional[bool] = None
    progress: Optional[int] = 0


@router.post("/interactive-lesson", response_model=InteractiveLessonResponse)
async def interactive_lesson_endpoint(request: InteractiveLessonRequest):
    """Unified interactive learning loop endpoint."""
    try:
        session_id = f"student_{request.student_id}_lesson_{request.lesson_id}"
        
        # If no text input is provided, we assume we need to LISTEN (STS Mode)
        # The orchestrator will handle the microphone activation.
        result = orchestrator.run_interactive_lesson(
            lesson_id=request.lesson_id,
            session_id=session_id,
            user_input=request.user_input,
            use_tts=request.enable_tts,
            use_stt=request.enable_stt
        )
        
        return InteractiveLessonResponse(
            success=result.get("success", False),
            state=result.get("state", "ERROR"),
            message=result.get("message", ""),
            audio_played=result.get("audio_played", False),
            prompt=result.get("prompt"),
            is_correct=result.get("is_correct"),
            progress=result.get("progress", 0)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Interactive lesson error: {str(e)}"
        )


# =========================
# VIDEO GENERATION ENDPOINTS
# =========================

@router.post("/video/generate", response_model=GenerateVideoResponse)
async def generate_video_endpoint(request: GenerateVideoRequest):
    """
    Generate an educational video synchronously.
    
    - If topic not provided, falls back to prompt.txt
    - If duration not provided, falls back to duration.txt
    - Returns only the final video path (no intermediate assets)
    """
    try:
        video_service = get_video_service()
        
        result = await video_service.generate_video_sync(
            topic=request.topic,
            duration=request.duration
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
        
        return GenerateVideoResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Video generation error: {str(e)}"
        )


@router.post("/video/generate-async", response_model=GenerateVideoAsyncResponse)
async def generate_video_async_endpoint(request: GenerateVideoAsyncRequest):
    """
    Generate an educational video asynchronously.
    
    Returns a job_id that can be used to poll for progress.
    Use GET /ai/video/status/{job_id} to check status.
    """
    try:
        video_service = get_video_service()
        
        result = await video_service.generate_video_async(
            topic=request.topic,
            duration=request.duration
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to queue video generation")
            )
        
        return GenerateVideoAsyncResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Async video generation error: {str(e)}"
        )


@router.get("/video/status/{job_id}", response_model=VideoStatusResponse)
async def get_video_status_endpoint(job_id: str):
    """
    Check the status of an async video generation job.
    
    Returns:
    - status: "queued", "processing", "completed", or "failed"
    - progress: 0-100 (only when processing)
    - video_path: Path to video (only when completed)
    """
    try:
        video_service = get_video_service()
        
        result = video_service.get_job_status(job_id)
        return VideoStatusResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Status check error: {str(e)}"
        )


@router.get("/video/download/{session_id}")
async def download_video_endpoint(session_id: str):
    """
    Download the generated video file.
    
    Returns the final MP4 video file as a streaming response.
    """
    try:
        video_service = get_video_service()
        
        # Get the video file path
        video_path = video_service.get_video_file_path(session_id)
        
        if not video_path or not video_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Video not found for session {session_id}"
            )
        
        # Return file as streaming response
        return FileResponse(
            path=video_path,
            media_type="video/mp4",
            filename=f"educational_video_{session_id}.mp4"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Download error: {str(e)}"
        )


@router.get("/video/list", response_model=VideoListResponse)
async def list_videos_endpoint(limit: int = 10):
    """
    List recently generated educational videos.
    
    Args:
        limit: Maximum number of videos to return (default: 10)
    """
    try:
        video_service = get_video_service()
        
        videos = video_service.list_generated_videos(limit=limit)
        
        return VideoListResponse(
            success=True,
            videos=videos,
            count=len(videos),
            message=f"Found {len(videos)} videos"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"List videos error: {str(e)}"
        )


@router.get("/video/health")
async def video_service_health():
    """Health check for video generation service."""
    try:
        video_service = get_video_service()
        
        # Test if service can access config files
        prompt = video_service._read_prompt_file()
        duration = video_service._read_duration_file()
        
        return {
            "status": "healthy",
            "service": "video_generation",
            "config": {
                "prompt_available": prompt is not None,
                "duration_available": duration is not None,
                "default_duration": duration
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "video_generation",
            "error": str(e)
        }