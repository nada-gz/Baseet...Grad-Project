from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
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
    """Unified video generation request (async by default)."""
    lesson_id: int
    student_id: int
    duration: Optional[float] = None


class VideoResponse(BaseModel):
    """Response for video generation and status."""
    success: bool
    job_id: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    video_path: Optional[str] = None
    video_url: Optional[str] = None
    session_id: Optional[str] = None
    message: str
    error: Optional[str] = None


# =========================
# SCAFFOLD MODELS
# =========================
class ScaffoldRequest(BaseModel):
    text: str

class ScaffoldResponse(BaseModel):
    success: bool
    found: Optional[str] = ""
    missing: Optional[list] = []
    next_prompt: Optional[str] = ""
    is_complete: bool = False
    connective_count: int = 0
    error: Optional[str] = None


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

@router.post("/video/generate", response_model=VideoResponse)
async def generate_video(request: GenerateVideoRequest):
    """
    Generate an educational video synchronously.
    
    - Fetches lesson topic and student context automatically
    - WAITS for generation to complete (synchronous)
    - Returns video_path and video_url directly in the response
    - Download with GET /ai/video/download/{session_id}
    """
    try:
        # 1. Fetch lesson content to use as topic
        lesson_data = fetch_lesson_by_id(request.lesson_id)
        if not lesson_data:
            raise HTTPException(status_code=404, detail=f"Lesson {request.lesson_id} not found")
        
        # Use simple content (usually Title: Description) as the topic for generation
        topic = lesson_data.get("content", "Educational Topic")
        
        # 2. Call video service synchronously
        video_service = get_video_service()
        result = await video_service.generate_video_sync(
            topic=topic,
            duration=request.duration,
            lesson_id=request.lesson_id,
            student_id=request.student_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Generation failed"))
        
        return VideoResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/video/download/{session_id}")
async def download_video(session_id: str):
    """Download the final MP4 video file."""
    try:
        video_service = get_video_service()
        video_path = video_service.get_video_file_path(session_id)
        
        if not video_path or not video_path.exists():
            raise HTTPException(status_code=404, detail=f"Video not found for session {session_id}")
        
        return FileResponse(
            path=video_path,
            media_type="video/mp4",
            filename=f"educational_video_{session_id}.mp4"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/video/health")
async def video_health():
    """Health check for video generation service."""
    try:
        video_service = get_video_service()
        prompt = video_service._read_prompt_file()
        duration = video_service._read_duration_file()
        
        return {
            "status": "healthy",
            "prompt_available": prompt is not None,
            "duration_available": duration is not None,
            "default_duration": duration
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
@router.post("/scaffold/narrative", response_model=ScaffoldResponse)
async def analyze_narrative(request: ScaffoldRequest):
    """Analyze a story narrative for C/S/P/E/R elements."""
    try:
        result = orchestrator.analyze_narrative_scaffold(request.text)
        return ScaffoldResponse(**result)
    except Exception as e:
        return ScaffoldResponse(success=False, error=str(e))
