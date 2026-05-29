import os
import json
import torch
import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types
import psycopg2
from typing import Dict, Any, List, Optional
import datetime

# Import cutter tools
try:
    from services.ai.cutter import (
        split_text_semantically,
        generate_title,
        normalize_arabic
    )
    CUTTER_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Warning: cutter.py not available: {e}")
    CUTTER_AVAILABLE = False

# Import explanation tools
try:
    from services.ai.explanation import (
        get_context_from_db as _get_context_impl,
        initialize_chat_session,
        generate_rag_answer_with_chat,
        prepare_system_instruction,
        generate_mcq,
        generate_batch_mcqs
    )
    EXPLANATION_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Warning: explanation.py not available: {e}")
    EXPLANATION_AVAILABLE = False
    # Define fallback functions
    def _get_context_impl(*args, **kwargs): return []
    def initialize_chat_session(*args, **kwargs): return None
    def generate_rag_answer_with_chat(*args, **kwargs): return "Error: Explanation module not available"
    def prepare_system_instruction(): return ""
    def generate_mcq(*args, **kwargs): return None
    def generate_batch_mcqs(*args, **kwargs): return []

# Import audio modules
try:
    from services.ai.TTS import TextPostProcessor, TTSGenerator
    TTS_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Warning: TTS.py not available: {e}")
    TTS_AVAILABLE = False

try:
    from services.ai.STT import EgyptianEar, JsonWriter
    STT_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Warning: STT.py not available: {e}")
    STT_AVAILABLE = False

load_dotenv()

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "autism_rag_db")
COLLECTION_NAME = "autism_content_arabic"
EMBEDDING_MODEL_NAME = 'intfloat/multilingual-e5-large'
GENERATION_MODEL = 'gemini-2.5-flash'
SHARED_FILE = os.getenv("SHARED_FILE", "shared_data.json")

# --- AI / RAG Initialization ---
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
device = "cuda" if torch.cuda.is_available() else "cpu"
embed_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)

# --- Session Storage ---
sessions: Dict[str, Dict[str, Any]] = {}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def save_questions_to_file(filename, new_questions, lesson_id, topic_title):
    """Appends new questions to a JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), "outputs", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    current_data = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    current_data = json.loads(content)
        except Exception as e:
            print(f"⚠️ Error reading {filename}: {e}")
            current_data = []

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "lesson_id": lesson_id,
        "topic": topic_title,
        "questions": new_questions
    }
    current_data.append(entry)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(current_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved {len(new_questions)} questions to {filename}")
    except Exception as e:
        print(f"❌ Error saving to {filename}: {e}")

# ==========================================
# SMART ORCHESTRATOR
# ==========================================

class SmartOrchestrator:
    def __init__(self):
        print("🚀 Initializing SmartOrchestrator...")
        self.gemini_client = gemini_client
        self.chroma_client = chroma_client
        self.embed_model = embed_model
        
        if TTS_AVAILABLE:
            self.text_processor = TextPostProcessor()
            self.voice = TTSGenerator()
        else:
            self.text_processor = None
            self.voice = None
        
        if STT_AVAILABLE:
            self.ear = EgyptianEar()
        else:
            self.ear = None
        
        self.chat_sessions: Dict[str, Any] = {}
        print("✅ SmartOrchestrator Ready!\n")
    
    def _count_words(self, text: str) -> int:
        if not text: return 0
        return len(text.strip().split())
    
    def handle_user_input(self, text: str, session_id: str = "default") -> Dict[str, Any]:
        if not text or not text.strip():
            return {"success": False, "error": "Empty input text", "response": None}
        
        word_count = self._count_words(text)
        try:
            if word_count > 10:
                return self._route_to_cutter(text)
            else:
                return self._route_to_explanation(text, session_id)
        except Exception as e:
            return {"success": False, "error": str(e), "response": None}
    
    def _route_to_cutter(self, text: str) -> Dict[str, Any]:
        if not CUTTER_AVAILABLE:
            return {"success": False, "error": "Cutter module not available", "response": None}
        try:
            chunks = split_text_semantically(text)
            formatted_chunks = []
            for i, chunk in enumerate(chunks, 1):
                formatted_chunks.append({
                    "chunk_id": i,
                    "title": generate_title(chunk),
                    "content": chunk
                })
            
            response_data = {
                "success": True,
                "agent": "cutter",
                "chunks": formatted_chunks,
                "response": formatted_chunks
            }
            
            # Save output
            outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
            os.makedirs(outputs_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(outputs_dir, f"cutter_output_{timestamp}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)
            
            return response_data
        except Exception as e:
            return {"success": False, "error": str(e), "response": None}
    
    def _route_to_explanation(self, text: str, session_id: str = "default") -> Dict[str, Any]:
        try:
            context_items = _get_context_impl(self.chroma_client, text, self.embed_model, k=3)
            context_str = "\n".join([f"- {item.get('original_content', {}).get('autism_friendly_ar', '')}" for item in context_items])
            
            if session_id not in self.chat_sessions:
                self.chat_sessions[session_id] = initialize_chat_session(self.gemini_client, prepare_system_instruction())
            
            explanation = generate_rag_answer_with_chat(
                chat_session=self.chat_sessions[session_id],
                query_text=text,
                context_string=context_str,
                is_clarification=False
            )
            return {"success": True, "message": explanation}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def process_voice_input(self, session_id: str = "default") -> Dict[str, Any]:
        if not STT_AVAILABLE or not self.ear:
            return {"success": False, "error": "STT not available", "transcription": None}
        try:
            transcribed_text = self.ear.listen()
            if not transcribed_text or not transcribed_text.strip():
                return {"success": False, "error": "No speech detected", "transcription": None}
            
            JsonWriter.save_transcription(transcribed_text)
            ai_response = self.handle_user_input(transcribed_text, session_id)
            return {"success": True, "transcription": transcribed_text, "ai_response": ai_response, "response": ai_response.get("response")}
        except Exception as e:
            return {"success": False, "error": str(e), "transcription": None}
    
    def speak_latest_response(self, text_to_speak: str) -> Dict[str, Any]:
        if not TTS_AVAILABLE or not self.voice:
            return {"success": False, "error": "TTS not available"}
        if not text_to_speak or text_to_speak.strip().startswith("❌"):
            print("⚠️ Skipping TTS for error message or empty text.")
            return {"success": False, "error": "Cannot speak error message"}

        try:
            normalized_text = self.text_processor.normalize_for_tts(text_to_speak)
            audio_base64 = self.voice.speak(normalized_text)
            if not audio_base64:
                return {"success": False, "error": "TTS engine returned no audio"}
            return {"success": True, "original_text": text_to_speak, "audio_base64": audio_base64}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==========================================
    # INTERACTIVE LESSON LOOP (UPDATED)
    # ==========================================
    
    def run_interactive_lesson(
        self, 
        lesson_id: int, 
        session_id: str,
        user_input: Optional[str] = None,
        use_tts: bool = True,
        use_stt: bool = True
    ) -> Dict[str, Any]:
        """
        Runs the interactive lesson.
        Flow: GREETING -> AWAITING_GREETING_RESPONSE -> LOADING -> EXPLAINING -> CONFIRMATION -> QUIZ
        """
        session_key = f"interactive_{session_id}"
        # Trigger Reset: ONLY if user_input is None AND we don't have a session, OR if explicitly requested (not yet implemented)
        # We check session state to avoid resetting during clarification
        if user_input is None:
            if session_key not in self.chat_sessions:
                print(f"🌟 Starting NEW session {session_key}")
            else:
                # If it's already in session and user_input is None, it's a re-entry/start call
                # We only reset if the state is COMPLETED or if we want a hard reset
                if self.chat_sessions[session_key]["state"] == "COMPLETED":
                     print(f"🔄 Resetting COMPLETED session {session_key}")
                     del self.chat_sessions[session_key]
        
        if session_key not in self.chat_sessions:
            self.chat_sessions[session_key] = {
                "state": "GREETING",
                "lesson_id": lesson_id,
                "lesson_content": None,
                "chunks": [],
                "current_chunk_idx": 0,
                "context_str": None,
                "current_mcq": None,
                "explanation_attempts": 0,
                "quiz_attempts": 0,
                "asked_questions": [],
                "previous_feedback": "",
                "progress": 0
            }
        
        session = self.chat_sessions[session_key]
        audio_played = False # Initialize to avoid UnboundLocalError
        
        try:
            # ==========================================
            # STATE: GREETING (Step 1)
            # ==========================================
            if session["state"] == "GREETING":
                greeting_msg = "إزيك يا حبيبي عامل إيه النهاردة؟"
                
                audio_played = False
                if use_tts and self.voice:
                    print("🔊 Speaking greeting...")
                    self.speak_latest_response(greeting_msg)
                    audio_played = True
                
                session["state"] = "AWAITING_GREETING_RESPONSE"
                
                return {
                    "success": True,
                    "state": "AWAITING_GREETING_RESPONSE",
                    "message": greeting_msg,
                    "audio_played": audio_played,
                    "needs_input": True
                }

            # ==========================================
            # STATE: AWAITING_GREETING_RESPONSE (Step 2)
            # ==========================================
            elif session["state"] == "AWAITING_GREETING_RESPONSE":
                # If these is NO user_input (None), it's a re-entry or double-mount start signal.
                # Do NOT return a duplicate message if we've already sent it.
                if user_input is None:
                    return {
                        "success": True, 
                        "state": session["state"], 
                        "message": "إزيك يا حبيبي عامل إيه النهاردة؟", 
                        "needs_input": True,
                        "audio_played": False
                    }

                # If the input is empty string, we stay here but return a friendly nudge
                if user_input.strip() == "":
                    if use_stt and STT_AVAILABLE and self.ear:
                        print("🎤 STT ACTIVATED: Listening for greeting response...")
                        voice_result = self.process_voice_input(session_id)
                        if voice_result.get("success"):
                            user_input = voice_result.get("transcription", "")
                            print(f"✅ Transcribed: {user_input}")
                        else:
                            error_msg = voice_result.get("error", "Unknown error")
                            return {
                                "success": False, 
                                "state": session["state"], 
                                "message": f"🎤 مسمعتش صوتك يا بطل، ممكن تقول تاني؟", 
                                "needs_input": True,
                                "audio_played": False
                            }
                    else:
                        # For web chat without STT, just return the greeting again if they hit chat without message
                        return {
                            "success": True, 
                            "state": session["state"], 
                            "message": "إزيك يا حبيبي عامل إيه النهاردة؟ 😊", 
                            "needs_input": True,
                            "audio_played": False
                        }
                
                # Received response (e.g., "Alhamdulillah" or "Fine")
                # Transition smoothly to LOADING
                session["state"] = "LOADING"
                # We do NOT return here. We let it fall through to LOADING/EXPLAINING immediately.
                # This ensures the child says "Fine" and immediately hears "Great, today we learn..."

            # ==========================================
            # STATE: LOADING
            # ==========================================
            if session["state"] == "LOADING":
                print(f"📚 Loading and cutting lesson {lesson_id}...")
                lesson_data = fetch_lesson_by_id(lesson_id)
                if not lesson_data:
                    return {"success": False, "state": "ERROR", "message": "❌ الدرس غير موجود", "needs_input": False}
                
                content = lesson_data["content"]
                # Cut content into parts
                if CUTTER_AVAILABLE:
                    session["chunks"] = split_text_semantically(content)
                    print(f"✂️ Lesson split into {len(session['chunks'])} parts.")
                else:
                    session["chunks"] = [content]
                
                session["current_chunk_idx"] = 0
                session["lesson_content"] = content
                session["state"] = "EXPLAINING"
            
            # ==========================================
            # STATE: EXPLAINING
            # ==========================================
            if session["state"] == "EXPLAINING":
                print("💬 Generating explanation...")
                # We use the global 'sessions' dict for the actual Gemini chat objects
                # because they are not JSON-serializable and shouldn't be in self.chat_sessions
                if session_key not in sessions:
                    sessions[session_key] = initialize_chat_session(self.gemini_client, prepare_system_instruction())
                
                chat_session = sessions[session_key]
                current_chunk = session["chunks"][session["current_chunk_idx"]]
                
                # Check if this is a clarification request (re-explaining same chunk)
                is_clarification = session["explanation_attempts"] > 0
                
                # Get RAG context for this specific chunk
                context_items = _get_context_impl(self.chroma_client, current_chunk, self.embed_model, k=3)
                session["context_str"] = "\n".join([item.get('original_content', {}).get('autism_friendly_ar', '') for item in context_items])

                explanation = generate_rag_answer_with_chat(
                    chat_session=chat_session,
                    query_text=current_chunk,
                    context_string=session["context_str"],
                    is_clarification=is_clarification
                )
                
                # Prepend a friendly bridge if this is the first explanation after greeting and NOT an error
                if session["explanation_attempts"] == 0 and not (explanation and explanation.strip().startswith("❌")):
                    explanation = f"يارب دايما بخير! 🌟\n{explanation}"

                session["explanation_attempts"] += 1
                
                audio_played = False
                if use_tts and self.voice:
                    print("🔊 Speaking explanation...")
                    self.speak_latest_response(explanation)
                    audio_played = True
                
                session["state"] = "AWAITING_CONFIRMATION"
                
                return {
                    "success": True,
                    "state": "AWAITING_CONFIRMATION",
                    "message": explanation,
                    "audio_played": audio_played,
                    "needs_input": True,
                    "prompt": "😊 فهمت يا بطل؟"
                }

            # ==========================================
            # STATE: AWAITING_CONFIRMATION
            # ==========================================
            elif session["state"] == "AWAITING_CONFIRMATION":
                if not user_input or user_input.strip() == "":
                    if use_stt and STT_AVAILABLE and self.ear:
                        print("🎤 STT ACTIVATED: Listening for confirmation...")
                        voice_result = self.process_voice_input(session_id)
                        if voice_result.get("success"):
                            user_input = voice_result.get("transcription", "")
                            print(f"✅ Transcribed: {user_input}")
                        else:
                            error_msg = voice_result.get("error", "Unknown error")
                            return {"success": False, "state": session["state"], "message": "🎤 مسمعتش صوتك يا حبيبي، ممكن تقول تاني؟", "needs_input": True, "audio_played": False}
                    else:
                        return {"success": True, "state": session["state"], "message": "😊 فهمت يا بطل؟ قولّي 'فهمت' أو 'مش فاهم'", "needs_input": True, "audio_played": False}
                
                user_input_lower = user_input.lower().strip()
                clarification_phrases = ['مش فاهم', 'مش فاهمة', 'تاني', 'اشرحلي تاني', 'ممكن توضيح', 'يعني ايه']
                confirmation_phrases = ['فهمت', 'تمام', 'خلاص', 'شكرا', 'كويس', 'اه', 'نعم']
                
                if any(p in user_input_lower for p in clarification_phrases):
                    session["state"] = "EXPLAINING"
                    return self.run_interactive_lesson(lesson_id, session_id, None, use_tts, use_stt)
                elif any(p in user_input_lower for p in confirmation_phrases):
                    session["state"] = "QUIZ_GENERATING"
                else:
                    return {"success": True, "state": session["state"], "message": "قولّي 'فهمت' أو 'مش فاهم'", "needs_input": True}

            # ==========================================
            # STATE: QUIZ_GENERATING
            # ==========================================
            if session["state"] == "QUIZ_GENERATING":
                print(f"❓ Generating quiz (Attempt {session['quiz_attempts'] + 1}/3)...")
                mcq = generate_mcq(self.gemini_client, session["context_str"], previous_questions=session["asked_questions"])
                
                if not mcq:
                    return {"success": False, "state": "ERROR", "message": "❌ حصل خطأ في توليد السؤال.", "needs_input": False}
                
                session["current_mcq"] = mcq
                session["asked_questions"].append(mcq["question_ar"])
                session["state"] = "QUIZ_ANSWERING"
                
                options = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(mcq["options_ar"])])
                intro = f"{session['previous_feedback']}\n\n" if session.get("previous_feedback") else ("✅ شاطر! قولّي الإجابة:\n" if use_stt else "✅ شاطر! خد السؤال ده:\n")
                msg = f"{intro}❓ {mcq['question_ar']}\n\n{options}"
                session["previous_feedback"] = "" # Clear buffer
                
                return {
                    "success": True, 
                    "state": "QUIZ_ANSWERING", 
                    "message": msg, 
                    "audio_played": audio_played, 
                    "quiz": mcq, 
                    "needs_input": True,
                    "part": session["current_chunk_idx"] + 1,
                    "total_parts": len(session["chunks"])
                }

            # ==========================================
            # STATE: QUIZ_ANSWERING
            # ==========================================
            elif session["state"] == "QUIZ_ANSWERING":
                if not user_input or user_input.strip() == "":
                    if use_stt and STT_AVAILABLE and self.ear:
                        print("🎤 STT ACTIVATED: Listening for quiz answer...")
                        voice_result = self.process_voice_input(session_id)
                        if voice_result.get("success"):
                            user_input = voice_result.get("transcription", "")
                        else:
                            return {"success": False, "state": session["state"], "message": "🎤 مسمعتش الإجابة، ممكن تقول الرقم تاني؟", "needs_input": True, "audio_played": False}
                    else:
                        return {"success": True, "state": session["state"], "message": ("قول رقم الإجابة الصحيحة يا بطل (1 أو 2 أو 3) 🎙️" if use_stt else "اكتب رقم الإجابة الصحيحة يا بطل (1 أو 2 أو 3) 📝"), "needs_input": True, "audio_played": False}

                mcq = session["current_mcq"]
                try:
                    choice_idx = int(user_input.strip()) - 1
                    if choice_idx < 0 or choice_idx >= len(mcq["options_ar"]): raise ValueError()
                    correct_idx = int(mcq["correct_answer_ar"]) - 1
                    is_correct = choice_idx == correct_idx
                except:
                    return {"success": False, "state": session["state"], "message": ("⚠️ قول رقم صحيح (1 أو 2 أو 3)" if use_stt else "⚠️ اكتب رقم صحيح (1 أو 2 أو 3)"), "needs_input": True}
                
                log_interaction_db({
                    "timestamp": datetime.datetime.now(), "user_input": user_input, "intent": "Quiz", 
                    "topic": session["lesson_content"], "question": mcq["question_ar"], 
                    "correct": is_correct, "topic_id": lesson_id
                })

                if is_correct:
                    # Update Progress
                    total_chunks = len(session["chunks"])
                    current_idx = session["current_chunk_idx"]
                    new_progress = int(((current_idx + 1) / total_chunks) * 100)
                    session["progress"] = new_progress
                    
                    print(f"📈 Updating progress for lesson {lesson_id}: {new_progress}%")
                    update_lesson_progress_db(lesson_id, new_progress)

                    if current_idx < total_chunks - 1:
                        # Move to next chunk
                        session["current_chunk_idx"] += 1
                        session["explanation_attempts"] = 0
                        session["quiz_attempts"] = 0
                        session["state"] = "EXPLAINING"
                        
                        success_msg = f"🎉 ممتاز يا بطل! إجابة صحيحة. 🌟\nمستعد للجزء اللي جاي؟\n(التقدم: {new_progress}%)"
                        
                        if use_tts and self.voice:
                            self.speak_latest_response(success_msg)
                        
                        return {
                            "success": True, 
                            "state": "EXPLAINING", 
                            "message": success_msg, 
                            "needs_input": True, 
                            "progress": new_progress,
                            "audio_played": True
                        }
                    else:
                        # Finished all chunks
                        session["state"] = "COMPLETED"
                        msg = "🎉 برافو عليك! إجابة ممتازة! 👏\nأنت بطل حقيقي وكملت الدرس بالكامل اليوم! 🌟"
                        # Phase 2: Save Review
                        try:
                            qs = generate_batch_mcqs(self.gemini_client, session["context_str"], count=4, previous_questions=session["asked_questions"])
                            if len(qs) >= 2:
                                save_questions_to_file("lesson_review.json", qs[:2], lesson_id, session.get("lesson_content"))
                                save_questions_to_file("milestone_review.json", qs[2:], lesson_id, session.get("lesson_content"))
                        except: pass
                else:
                    session["quiz_attempts"] += 1
                    if session["quiz_attempts"] < 3:
                        session["state"] = "QUIZ_GENERATING"
                        session["previous_feedback"] = f"معلش حاول تاني! {mcq.get('gentle_explanation_if_wrong', '')}"
                        return self.run_interactive_lesson(lesson_id, session_id, None, use_tts, use_stt)
                    else:
                        # Too many attempts, move on anyway or end?
                        # Let's move to next part but with a gentle message if it's not the last
                        total_chunks = len(session["chunks"])
                        current_idx = session["current_chunk_idx"]
                        new_progress = int(((current_idx + 1) / total_chunks) * 100)
                        session["progress"] = new_progress
                        update_lesson_progress_db(lesson_id, new_progress)
                        
                        if current_idx < total_chunks - 1:
                            session["current_chunk_idx"] += 1
                            session["explanation_attempts"] = 0
                            session["quiz_attempts"] = 0
                            session["state"] = "EXPLAINING"
                            msg = f"{mcq.get('gentle_explanation_if_wrong', '')}\nمش مشكلة، يلا نشوف الجزء التاني ونحاول فيه! 😊"
                            if use_tts and self.voice:
                                self.speak_latest_response(msg)
                            return {
                                "success": True, 
                                "state": "EXPLAINING", 
                                "message": msg, 
                                "needs_input": True, 
                                "progress": new_progress,
                                "audio_played": True
                            }
                        else:
                            session["state"] = "COMPLETED"
                            msg = f"مش مشكلة! {mcq.get('gentle_explanation_if_wrong', '')}\nلقد بذلت مجهود رائع اليوم! 🌟"

                audio_played = False
                if use_tts and self.voice:
                    self.speak_latest_response(msg)
                    audio_played = True
                
                if session["state"] == "COMPLETED":
                    del self.chat_sessions[session_key]

                return {
                    "success": True, 
                    "state": session["state"], 
                    "message": msg, 
                    "audio_played": audio_played, 
                    "is_correct": is_correct, 
                    "needs_input": session["state"] != "COMPLETED",
                    "progress": session.get("progress", 0)
                }

            return {"success": False, "state": "ERROR", "message": f"Unknown State: {session['state']}"}

        except Exception as e:
            import traceback
            print(f"❌ Error in run_interactive_lesson: {e}")
            traceback.print_exc()
            return {
                "success": False, 
                "state": "ERROR", 
                "message": "يا بطل، حصلت مشكلة صغيرة عندي. ممكن تحاول تاني؟ 😅",
                "technical_error": str(e)
            }

    # ==========================================
    # NARRATIVE SCAFFOLD (NEW)
    # ==========================================
    def analyze_narrative_scaffold(self, text: str) -> Dict[str, Any]:
        """
        Analyzes text for Story Grammar (C/S/P/E/R) and Causal Connectives.
        Uses a robust prompt to minimize false positives and capture subtle child narratives.
        """
        if not text or not text.strip():
            return {"success": False, "error": "Empty text"}

        # 1. Count Causal Connectives (Expanded Arabic list)
        causal_words = [
            "عشان", "علشان", "لأن", "بسبب", "فـ", "وبالتالي", "لذلك", "وبعدين", 
            "فجأة", "عشان كدة", "في الآخر", "لما", "وقت ما"
        ]
        connective_count = 0
        text_lower = text.lower()
        for word in causal_words:
            connective_count += text_lower.count(word)

        # 2. Use Gemini with a high-accuracy narrative analysis prompt
        prompt = f"""
        You are an expert Speech-Language Pathologist specialized in Narrative Analysis for children (Story Grammar).
        Analyze the following Arabic story transcript (transcribed from speech) for these 5 elements:
        
        ELEMENTS CRITERIA:
        - Character (C): Any person, animal, or living robot mentioned. (e.g. "أنا", "بسيط", "صاحبي")
        - Setting (S): Explicit location or time mention. Be conservative; don't assume a setting unless mentioned (e.g. "في المدرسة", "يوم الجمعة", "على البحر").
        - Problem (P): A specific challenge, conflict, or something going wrong. (e.g. "العجلة اتكسرت", "ضاعت مني اللعبة", "كنت زعلان")
        - Event (E): Action taken to solve the problem or a core activity. (e.g. "رحت أصلحها", "فضلت أدور عليها", "لعبنا بالكورة")
        - Resolution (R): The outcome or how things ended. (e.g. "لقيتها في الآخر", "بقينا مبسوطين", "روحت البيت")

        INSTRUCTIONS:
        1. Identify which elements are TRULY present. Do not guess.
        2. If the child mentions a problem like "I lost my toy", that IS a Problem (P).
        3. If the child describes an action like "I started looking", that IS an Event (E).
        4. Generate a very friendly follow-up question in Arabic (Egyptian dialect preferred) to ask about ONE missing element to help them complete the story.

        OUTPUT FORMAT (JSON):
        {{
          "found": "C,P,E", // String of found elements
          "missing": ["Setting", "Resolution"], // Array of full names
          "prompt": "شاطر أوي! وايه اللي حصل في الآخر؟", // Friendly follow-up
          "is_complete": false // true if all 5 are present
        }}

        STORY TRANSCRIPT: "{text}"
        """
        
        try:
            response = self.gemini_client.models.generate_content(
                model=GENERATION_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1 # Low temperature for more consistent analysis
                )
            )
            analysis = json.loads(response.text)
            
            # Final sanity check: ensure 'found' matches 'missing' logic
            found_list = analysis.get("found", "").split(',')
            found_list = [f.strip() for f in found_list if f.strip()]
            
            return {
                "success": True,
                "found": ",".join(found_list),
                "missing": analysis.get("missing", []),
                "next_prompt": analysis.get("prompt", "كمل حكايتك يا بطل وايه حصل تاني؟"),
                "is_complete": analysis.get("is_complete", False),
                "connective_count": connective_count
            }
        except Exception as e:
            print(f"❌ Scaffold Error: {e}")
            return {
                "success": False, 
                "error": str(e),
                "connective_count": connective_count
            }

# ==========================================
# HELPERS & EXPORTS
# ==========================================
orchestrator = SmartOrchestrator()
def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if db_url.startswith("postgresql+psycopg://"): db_url = db_url.replace("postgresql+psycopg://", "postgresql://")
    return psycopg2.connect(db_url)
def fetch_lesson_by_id(lid):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. Try student-specific lessons table first
        cur.execute("SELECT id, title, description FROM lessons WHERE id = %s", (lid,))
        row = cur.fetchone()
        
        if row:
            content = f"{row[1]}: {row[2]}" if row[2] else row[1]
            cur.close(); conn.close()
            return {"id": row[0], "content": content}
        
        # 2. Try master content_lessons table
        cur.execute("SELECT id, title, description FROM content_lessons WHERE id = %s", (lid,))
        row = cur.fetchone()
        
        cur.close(); conn.close()
        
        if row:
            content = f"{row[1]}: {row[2]}" if row[2] else row[1]
            return {"id": row[0], "content": content}
            
        return None
    except Exception as e:
        print(f"❌ Error fetching lesson {lid}: {e}")
        return None
def log_interaction_db(d):
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("INSERT INTO log_table (timestamp, user_input, intent, topic, question, correct, topic_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (d.get("timestamp"), d.get("user_input"), d.get("intent"), d.get("topic"), d.get("question"), d.get("correct"), d.get("topic_id")))
        conn.commit(); cur.close(); conn.close()
    except: pass

def update_lesson_progress_db(lesson_id, progress):
    """Updates the progress and status of a lesson in the database."""
    try:
        conn = get_db_connection(); cur = conn.cursor()
        # Also update status to 'in_progress' if progress > 0 and 'completed' if progress == 100
        status = "in_progress"
        if progress >= 100:
            status = "completed"
        
        cur.execute("UPDATE lessons SET progress = %s, status = %s WHERE id = %s", (progress, status, lesson_id))
        conn.commit(); cur.close(); conn.close()
        print(f"✅ DB: Lesson {lesson_id} updated to {progress}% ({status})")
    except Exception as e:
        print(f"❌ DB Error updating progress: {e}")
def process_text_input(t, s="default"): return orchestrator.handle_user_input(t, s)
def process_voice_input(s="default"): return orchestrator.process_voice_input(s)
def speak_text(t): return orchestrator.speak_latest_response(t)
# Legacy Fallbacks
def get_context_from_db(q, k=3): return _get_context_impl(chroma_client, q, embed_model, k)
def generate_explanation(t, c, i=False): return orchestrator._route_to_explanation(t, "legacy").get("message")
def generate_mcq_ai(c): return generate_mcq(gemini_client, c)
def generate_feedback(q, c, u, i): return "👏 برافو!" if i else f"😊 الإجابة: {c}"