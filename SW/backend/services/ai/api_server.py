"""
FastAPI Server for SmartOrchestrator
Provides HTTP endpoints for STT, TTS, and AI processing.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn

# Import orchestrator
from ai_service import orchestrator, process_text_input, process_voice_input, speak_text

# ==========================================
# FASTAPI APP SETUP
# ==========================================

app = FastAPI(
    title="SmartOrchestrator API",
    description="Rule-based AI orchestrator with STT/TTS integration",
    version="1.0.0"
)

# CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class TextInputRequest(BaseModel):
    """Request model for text input."""
    text: str
    session_id: Optional[str] = "default"


class VoiceInputRequest(BaseModel):
    """Request model for voice input."""
    session_id: Optional[str] = "default"


class TTSRequest(BaseModel):
    """Request model for TTS."""
    text: str


class ChunkResponse(BaseModel):
    """Response model for a text chunk."""
    chunk_id: int
    title: str
    content: str


class AIResponse(BaseModel):
    """Generic AI response model."""
    success: bool
    agent: Optional[str] = None
    word_count: Optional[int] = None
    response: Any = None
    error: Optional[str] = None
    num_chunks: Optional[int] = None
    chunks: Optional[List[Dict[str, Any]]] = None
    num_context_items: Optional[int] = None


# ==========================================
# HEALTH CHECK ENDPOINT
# ==========================================

@app.get("/")
def root():
    """Root endpoint - health check."""
    return {
        "status": "online",
        "service": "SmartOrchestrator API",
        "version": "1.0.0",
        "endpoints": {
            "text_input": "/api/text",
            "voice_input": "/api/voice",
            "tts": "/api/speak",
            "health": "/health"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "orchestrator": "running",
        "modules": {
            "cutter": orchestrator is not None,
            "explanation": True,
            "tts": orchestrator.voice is not None if orchestrator else False,
            "stt": orchestrator.ear is not None if orchestrator else False
        }
    }


# ==========================================
# TEXT INPUT ENDPOINT
# ==========================================

@app.post("/api/text", response_model=AIResponse)
def process_text(request: TextInputRequest):
    """
    Process text input through SmartOrchestrator.
    
    Rule-based routing:
    - If word_count > 10 → Cutter (text chunking)
    - Otherwise → Explanation with RAG
    
    Args:
        request: TextInputRequest with text and optional session_id
        
    Returns:
        AI response with appropriate routing
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text input is required")
    
    try:
        result = process_text_input(request.text, request.session_id)
        return AIResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


# ==========================================
# VOICE INPUT ENDPOINT (STT)
# ==========================================

@app.post("/api/voice")
def process_voice(request: VoiceInputRequest):
    """
    Process voice input using STT module.
    
    Flow:
    1. Captures audio via microphone
    2. Transcribes using Wav2Vec2 (Egyptian Arabic)
    3. Saves to shared_data.json
    4. Routes through SmartOrchestrator
    
    Args:
        request: VoiceInputRequest with optional session_id
        
    Returns:
        Dictionary with transcription and AI response
    """
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


# ==========================================
# TTS ENDPOINT (Output)
# ==========================================

@app.post("/api/speak")
def text_to_speech(request: TTSRequest, background_tasks: BackgroundTasks):
    """
    Convert text to speech using TTS module.
    
    Flow:
    1. Normalizes Arabic text for TTS
    2. Converts to speech using ElevenLabs
    3. Plays audio
    
    Args:
        request: TTSRequest with text to speak
        background_tasks: FastAPI background tasks
        
    Returns:
        Success status
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required for TTS")
    
    try:
        # Run TTS in background to avoid blocking
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


# ==========================================
# ADVANCED ENDPOINTS
# ==========================================

@app.post("/api/chat")
def chat_endpoint(request: TextInputRequest):
    """
    Chat endpoint with session management.
    Similar to /api/text but emphasizes conversational aspect.
    """
    return await process_text(request)


@app.get("/api/sessions/{session_id}")
def get_session_info(session_id: str):
    """
    Get information about a chat session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session status
    """
    if session_id in orchestrator.chat_sessions:
        return {
            "session_id": session_id,
            "exists": True,
            "message": "Session is active"
        }
    else:
        return {
            "session_id": session_id,
            "exists": False,
            "message": "Session not found"
        }


@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    """
    Delete a chat session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Deletion status
    """
    if session_id in orchestrator.chat_sessions:
        del orchestrator.chat_sessions[session_id]
        return {
            "success": True,
            "message": f"Session {session_id} deleted"
        }
    else:
        raise HTTPException(status_code=404, detail="Session not found")


# ==========================================
# TESTING ENDPOINTS
# ==========================================

@app.post("/api/test/cutter")
def test_cutter(request: TextInputRequest):
    """
    Force routing to cutter agent (testing only).
    """
    try:
        result = orchestrator._route_to_cutter(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cutter test error: {str(e)}")


@app.post("/api/test/explanation")
def test_explanation(request: TextInputRequest):
    """
    Force routing to explanation agent (testing only).
    """
    try:
        result = orchestrator._route_to_explanation(request.text, request.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation test error: {str(e)}")


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting SmartOrchestrator API Server")
    print("="*60)
    print("\n📚 API Documentation available at: http://localhost:8000/docs")
    print("📊 Alternative docs at: http://localhost:8000/redoc")
    print("\n✨ Endpoints:")
    print("   • POST /api/text - Process text input")
    print("   • POST /api/voice - Process voice input (STT)")
    print("   • POST /api/speak - Convert text to speech (TTS)")
    print("   • GET  /health - Health check")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
