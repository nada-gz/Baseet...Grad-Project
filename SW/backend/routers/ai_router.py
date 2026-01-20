from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import datetime

from services.ai.ai_service import (
    sessions,
    fetch_lesson_by_id,
    orchestrator,
    process_text_input,
    process_voice_input,
    speak_text
)

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
        state=result.get("state", "error")
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
        state=result.get("state", "error")
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
        
        return {
            "success": True,
            "message": "Audio generated and playing",
            "original_text": request.text,
            "normalized_text": result.get("normalized_text")
        }
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
    enable_stt: bool = False


class InteractiveLessonResponse(BaseModel):
    """Response model for interactive lesson state."""
    success: bool
    state: str
    message: str
    audio_played: bool = False
    needs_input: bool = False
    prompt: Optional[str] = None
    is_correct: Optional[bool] = None


@router.post("/interactive-lesson", response_model=InteractiveLessonResponse)
async def interactive_lesson_endpoint(request: InteractiveLessonRequest):
    """Unified interactive learning loop endpoint."""
    try:
        session_id = f"student_{request.student_id}_lesson_{request.lesson_id}"
        
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
            needs_input=result.get("needs_input", False),
            prompt=result.get("prompt"),
            is_correct=result.get("is_correct")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Interactive lesson error: {str(e)}"
        )