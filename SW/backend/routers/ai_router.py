from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import datetime

from services.ai.ai_service import (
    sessions,
    fetch_lesson_by_id,
    get_context_from_db,
    generate_explanation,
    generate_mcq_ai,
    generate_feedback,
    log_interaction_db,
    CLARIFICATION_PHRASES,
    CONFIRMATION_PHRASES,
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
# START LESSON (Frontend calls this first)
# =========================
@router.post("/lesson/start", response_model=BotResponse)
async def start_lesson(request: StartLessonRequest):
    student_id = str(request.student_id)

    # Load the specific lesson only
    lesson_data = fetch_lesson_by_id(request.lesson_id)
    if not lesson_data:
        return BotResponse(message="❌ الدرس غير موجود", state="error")

    sessions[student_id] = {
        "status": "start",
        "topic_id": lesson_data["id"],
        "topic_content": lesson_data["content"],
        "context_str": "",
        "current_mcq": None
    }

    return await chat_lesson(
        ChatRequest(
            lesson_id=request.lesson_id,
            student_id=request.student_id,
            message=""
        )
    )


# =========================
# AI CHAT (Main Loop)
# =========================
@router.post("/lesson/chat", response_model=BotResponse)
async def chat_lesson(request: ChatRequest):
    student_id = str(request.student_id)
    user_input = request.message.strip()

    if student_id not in sessions:
        return BotResponse(
            message="❌ برجاء بدء الدرس أولاً من صفحة الدروس",
            state="error"
        )

    session = sessions[student_id]

    # ==================================================
    # CASE A: START / EXPLAIN LESSON
    # ==================================================
    if session["status"] == "start":
        lesson_data = fetch_lesson_by_id(request.lesson_id)
        if not lesson_data:
            return BotResponse(message="❌ الدرس غير موجود", state="error")

        context = get_context_from_db(lesson_data["content"])
        session["context_str"] = "\n".join(
            c["original_content"].get("autism_friendly_ar", "")
            for c in context
        )

        explanation = generate_explanation(lesson_data["content"], context)

        session["status"] = "awaiting_confirmation"

        log_interaction_db({
            "timestamp": datetime.datetime.now(),
            "user_input": "SYSTEM_START",
            "intent": "Lesson_Start",
            "topic": lesson_data["content"],
            "topic_id": lesson_data["id"]
        })

        return BotResponse(
            message=(
                f"📝 درس جديد:\n{lesson_data['content']}\n\n"
                f"{explanation}\n\n"
                "😊 فهمت يا بطل؟"
            ),
            state=session["status"]
        )

    # ==================================================
    # CASE B: AWAITING CONFIRMATION
    # ==================================================
    elif session["status"] == "awaiting_confirmation":
        is_clarification = any(p in user_input for p in CLARIFICATION_PHRASES)
        is_confirmation = any(p in user_input for p in CONFIRMATION_PHRASES)

        if is_clarification:
            explanation = generate_explanation(
                session["topic_content"],
                [{"original_content": {"autism_friendly_ar": session["context_str"]}}],
                is_clarification=True
            )

            return BotResponse(
                message=f"{explanation}\n\nها؟ كده أوضح؟",
                state=session["status"]
            )

        elif is_confirmation:
            mcq = generate_mcq_ai(session["context_str"])
            if not mcq:
                return BotResponse(
                    message="❌ حصل خطأ، حاول تاني.",
                    state=session["status"]
                )

            session["current_mcq"] = mcq
            session["status"] = "awaiting_mcq"

            options = "\n".join(
                f"{i+1}. {opt}" for i, opt in enumerate(mcq["options_ar"])
            )

            return BotResponse(
                message=(
                    "✅ شاطر! خد السؤال ده:\n\n"
                    f"❓ {mcq['question_ar']}\n\n"
                    f"{options}\n\n"
                    "اكتب رقم الإجابة (1 أو 2 أو 3)."
                ),
                state=session["status"]
            )

        else:
            return BotResponse(
                message=(
                    "قولّي 'فهمت' لو تمام 👌\n"
                    "أو 'مش فاهم' لو تحب أشرح تاني 😊"
                ),
                state=session["status"]
            )

    # ==================================================
    # CASE C: AWAITING MCQ ANSWER
    # ==================================================
    elif session["status"] == "awaiting_mcq":
        mcq = session["current_mcq"]

        try:
            choice_idx = int(user_input) - 1
            correct_idx = int(mcq["correct_answer_ar"]) - 1
            is_correct = choice_idx == correct_idx
            user_choice_text = mcq["options_ar"][choice_idx]
        except Exception:
            is_correct = False
            user_choice_text = "Invalid"

        feedback = generate_feedback(
            mcq["question_ar"],
            mcq["options_ar"][correct_idx],
            user_choice_text,
            is_correct
        )

        log_interaction_db({
            "timestamp": datetime.datetime.now(),
            "user_input": user_input,
            "intent": "MCQ_Attempt",
            "topic": session["topic_content"],
            "question": mcq["question_ar"],
            "correct": is_correct,
            "correct_answer": mcq["options_ar"][correct_idx],
            "user_choice": user_choice_text,
            "topic_id": session["topic_id"]
        })

        session["status"] = "finished"

        return BotResponse(
            message=(
                f"{feedback}\n\n"
                "🎉 انتهى الدرس! ارجع لصفحة الدروس لاختيار درس آخر."
            ),
            state=session["status"]
        )

    # ==================================================
    # CASE D: LESSON FINISHED (ANY MESSAGE)
    # ==================================================
    elif session["status"] == "finished":
        return BotResponse(
            message="🎉 انتهى الدرس! ارجع لصفحة الدروس لاختيار درس آخر.",
            state="finished"
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
    """
    Process voice input using STT module.
    
    Flow:
    1. Captures audio via microphone
    2. Transcribes using Wav2Vec2 (Egyptian Arabic)
    3. Saves to shared_data.json
    4. Routes through SmartOrchestrator
    
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


@router.post("/speak")
async def text_to_speech_endpoint(request: TTSRequest):
    """
    Convert text to speech using TTS module.
    
    Flow:
    1. Normalizes Arabic text for TTS
    2. Converts to speech using ElevenLabs
    3. Plays audio
    
    Returns:
        Success status with normalized text
    """
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
    """
    Process text input through SmartOrchestrator.
    
    Rule-based routing:
    - If word_count > 10 → Cutter (text chunking)
    - Otherwise → Explanation with RAG
    
    Returns:
        AI response with appropriate routing
    """
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

