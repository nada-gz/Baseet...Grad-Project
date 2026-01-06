from fastapi import APIRouter
from pydantic import BaseModel
import datetime

from services.ai.ai_service import (
    sessions,
    fetch_next_topic,
    get_last_progress,
    get_context_from_db,
    generate_explanation,
    generate_mcq_ai,
    generate_feedback,
    log_interaction_db,
    CLARIFICATION_PHRASES,
    CONFIRMATION_PHRASES
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

    last_topic_id = get_last_progress()
    sessions[student_id] = {
        "status": "start",  # start | awaiting_confirmation | awaiting_mcq
        "topic_id": last_topic_id,
        "topic_content": "",
        "context_str": "",
        "current_mcq": None
    }

    # Trigger first topic immediately
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

    # -------------------------
    # Ensure session exists
    # -------------------------
    if student_id not in sessions:
        last_topic_id = get_last_progress()
        sessions[student_id] = {
            "status": "start",
            "topic_id": last_topic_id,
            "topic_content": "",
            "context_str": "",
            "current_mcq": None
        }

    session = sessions[student_id]
    response_text = ""

    # ==================================================
    # CASE A: START / NEXT TOPIC
    # ==================================================
    if session["status"] == "start":
        topic_data = fetch_next_topic(session["topic_id"])

        if not topic_data:
            return BotResponse(
                message="🎉 خلصنا كل الدروس النهاردة! شاطر جداً.",
                state="finished"
            )

        session["topic_id"] = topic_data["id"]
        session["topic_content"] = topic_data["content"]

        context = get_context_from_db(topic_data["content"])
        session["context_str"] = "\n".join(
            c["original_content"].get("autism_friendly_ar", "")
            for c in context
        )

        explanation = generate_explanation(topic_data["content"], context)

        response_text = (
            f"📝 موضوع جديد:\n{topic_data['content']}\n\n"
            f"{explanation}\n\n"
            "😊 فهمت يا بطل؟"
        )

        session["status"] = "awaiting_confirmation"

        log_interaction_db({
            "timestamp": datetime.datetime.now(),
            "user_input": "SYSTEM_START",
            "intent": "New_Topic",
            "topic": topic_data["content"],
            "topic_id": topic_data["id"]
        })

    # ==================================================
    # CASE B: AWAITING CONFIRMATION
    # ==================================================
    elif session["status"] == "awaiting_confirmation":
        is_clarification = any(p in user_input for p in CLARIFICATION_PHRASES)
        is_confirmation = any(p in user_input for p in CONFIRMATION_PHRASES)

        if is_clarification:
            explanation = generate_explanation(
                session["topic_content"],
                [{
                    "original_content": {
                        "autism_friendly_ar": session["context_str"]
                    }
                }],
                is_clarification=True
            )

            response_text = f"{explanation}\n\nها؟ كده أوضح؟"

            log_interaction_db({
                "timestamp": datetime.datetime.now(),
                "user_input": user_input,
                "intent": "Clarification",
                "topic": session["topic_content"],
                "topic_id": session["topic_id"]
            })

        elif is_confirmation:
            mcq = generate_mcq_ai(session["context_str"])

            if mcq:
                session["current_mcq"] = mcq
                session["status"] = "awaiting_mcq"

                options = "\n".join(
                    f"{i + 1}. {opt}"
                    for i, opt in enumerate(mcq["options_ar"])
                )

                response_text = (
                    "✅ شاطر! خد السؤال ده:\n\n"
                    f"❓ {mcq['question_ar']}\n\n"
                    f"{options}\n\n"
                    "اكتب رقم الإجابة (1 أو 2 أو 3)."
                )
            else:
                session["status"] = "start"
                return await chat_lesson(request)

        else:
            response_text = (
                "قولّي 'فهمت' لو تمام 👌\n"
                "أو 'مش فاهم' لو تحب أشرح تاني 😊"
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

        session["status"] = "start"

        next_topic = await chat_lesson(
            ChatRequest(
                lesson_id=request.lesson_id,
                student_id=request.student_id,
                message=""
            )
        )

        response_text = (
            f"{feedback}\n\n"
            "🔄 نكمل على اللي بعده 👇\n\n"
            "----------------\n"
            f"{next_topic.message}"
        )

    return BotResponse(
        message=response_text,
        state=session["status"]
    )
