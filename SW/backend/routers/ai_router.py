from fastapi import APIRouter
from pydantic import BaseModel
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
import datetime

router = APIRouter(prefix="/ai", tags=["AI"])

# --- Pydantic Models ---
class UserRequest(BaseModel):
    user_id: str
    message: str = ""

class BotResponse(BaseModel):
    response: str
    state: str

# --- AI Chat Endpoint ---
@router.post("/chat", response_model=BotResponse)
async def chat_endpoint(request: UserRequest):
    user_id = request.user_id
    user_input = request.message.strip()

    # Initialize session if new
    if user_id not in sessions:
        last_id = get_last_progress()
        sessions[user_id] = {
            "status": "start",           # start, awaiting_confirmation, awaiting_mcq
            "topic_id": last_id,
            "topic_content": "",
            "context_str": "",
            "current_mcq": None
        }

    session = sessions[user_id]
    response_text = ""

    # --- CASE A: START / NEXT TOPIC ---
    if session["status"] == "start":
        topic_data = fetch_next_topic(session["topic_id"])
        if not topic_data:
            return BotResponse(response="🎉 خلصنا كل الدروس النهاردة! شاطر جداً.", state="finished")

        # Save Topic Info
        session["topic_id"] = topic_data["id"]
        session["topic_content"] = topic_data["content"]

        # RAG Context
        context = get_context_from_db(topic_data["content"])
        session["context_str"] = "\n".join([c['original_content'].get('autism_friendly_ar', '') for c in context])

        # Generate explanation
        explanation = generate_explanation(topic_data["content"], context)
        response_text = f"📝 موضوع جديد: {topic_data['content']}\n\n{explanation}\n\n😊 فهمت يا بطل؟"
        session["status"] = "awaiting_confirmation"

        # Log start
        log_interaction_db({
            "timestamp": datetime.datetime.now(),
            "user_input": "SYSTEM_START",
            "intent": "New_Topic",
            "topic": topic_data["content"],
            "topic_id": topic_data["id"]
        })

    # --- CASE B: AWAITING CONFIRMATION ---
    elif session["status"] == "awaiting_confirmation":
        is_clarification = any(p in user_input for p in CLARIFICATION_PHRASES)
        is_confirmation = any(p in user_input for p in CONFIRMATION_PHRASES)

        if is_clarification:
            new_explanation = generate_explanation(
                session["topic_content"],
                [{"original_content": {"autism_friendly_ar": session["context_str"]}}],
                is_clarification=True
            )
            response_text = f"{new_explanation}\n\nها؟ كده أوضح؟"

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
                options_str = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(mcq['options_ar'])])
                response_text = f"✅ شاطر! طب خد السؤال ده:\n\n❓ {mcq['question_ar']}\n\n{options_str}\n\nاكتب رقم الإجابة (1 أو 2 أو 3)."
                session["status"] = "awaiting_mcq"
            else:
                # Skip to next topic if MCQ fails
                session["status"] = "start"
                return await chat_endpoint(request)

        else:
            response_text = "حبيبي، قول 'فهمت' لو تمام، أو 'مش فاهم' لو عايزني أشرح تاني."

    # --- CASE C: AWAITING MCQ ANSWER ---
    elif session["status"] == "awaiting_mcq":
        mcq = session["current_mcq"]
        try:
            choice_idx = int(user_input) - 1
            correct_idx = int(mcq['correct_answer_ar']) - 1
            is_correct = (choice_idx == correct_idx)
            user_choice_text = mcq['options_ar'][choice_idx] if 0 <= choice_idx < len(mcq['options_ar']) else "Invalid"
        except:
            is_correct = False
            user_choice_text = "Invalid"

        feedback = generate_feedback(
            mcq['question_ar'],
            mcq['options_ar'][int(mcq['correct_answer_ar']) - 1],
            user_choice_text,
            is_correct
        )

        # Log MCQ result
        log_interaction_db({
            "timestamp": datetime.datetime.now(),
            "user_input": user_input,
            "intent": "MCQ_Attempt",
            "topic": session["topic_content"],
            "question": mcq['question_ar'],
            "correct": is_correct,
            "correct_answer": mcq['options_ar'][int(mcq['correct_answer_ar']) - 1],
            "user_choice": user_choice_text,
            "topic_id": session["topic_id"]
        })

        response_text = f"{feedback}\n\n🔄 جاري الانتقال للموضوع التالي..."

        # Reset to next topic
        session["status"] = "start"
        next_topic_response = await chat_endpoint(request)
        response_text += f"\n\n----------------\n{next_topic_response.response}"

    return BotResponse(response=response_text, state=session["status"])
