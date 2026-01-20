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
        generate_batch_mcqs  # <--- NEW IMPORT for Phase 2
    )
    EXPLANATION_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Warning: explanation.py not available: {e}")
    EXPLANATION_AVAILABLE = False
    # Define fallback functions
    def _get_context_impl(*args, **kwargs):
        return []
    def initialize_chat_session(*args, **kwargs):
        return None
    def generate_rag_answer_with_chat(*args, **kwargs):
        return "Error: Explanation module not available"
    def prepare_system_instruction():
        return ""
    def generate_mcq(*args, **kwargs):
        return None
    def generate_batch_mcqs(*args, **kwargs):
        return []

# Import audio modules
try:
    from services.ai.TTS import TextPostProcessor, voice
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
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "autism_rag_db")  # Full path to local autism_rag_db
COLLECTION_NAME = "autism_content_arabic"
EMBEDDING_MODEL_NAME = 'intfloat/multilingual-e5-large'
GENERATION_MODEL = 'gemini-2.0-flash-exp'
SHARED_FILE = os.getenv("SHARED_FILE", "shared_data.json")

# --- AI / RAG Initialization ---
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
device = "cuda" if torch.cuda.is_available() else "cpu"
embed_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)

# --- Session Storage ---
sessions: Dict[str, Dict[str, Any]] = {}

# ==========================================
# HELPER FUNCTIONS (PHASE 2)
# ==========================================

def save_questions_to_file(filename, new_questions, lesson_id, topic_title):
    """Appends new questions to a JSON file."""
    # Ensure outputs directory exists
    filepath = os.path.join(os.path.dirname(__file__), "outputs", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    current_data = []
    
    # 1. Load existing data if file exists
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    current_data = json.loads(content)
        except Exception as e:
            print(f"⚠️ Error reading {filename}: {e}")
            current_data = []

    # 2. Append new entry
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "lesson_id": lesson_id,
        "topic": topic_title,
        "questions": new_questions
    }
    current_data.append(entry)
    
    # 3. Save back
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(current_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved {len(new_questions)} questions to {filename}")
    except Exception as e:
        print(f"❌ Error saving to {filename}: {e}")

# ==========================================
# SMART ORCHESTRATOR (RULE-BASED)
# ==========================================

class SmartOrchestrator:
    """
    Secure, rule-based orchestrator that manages interactions between:
    - Text Processing Agent (cutter.py)
    - Explanation Agent (explanation.py)
    - Audio Modules (TTS.py, STT.py)
    
    Uses Python logic for routing (NO LLM calls for routing) to save tokens and increase security.
    """
    
    def __init__(self):
        """Initialize the SmartOrchestrator with all necessary components."""
        print("🚀 Initializing SmartOrchestrator...")
        
        # AI/RAG components
        self.gemini_client = gemini_client
        self.chroma_client = chroma_client
        self.embed_model = embed_model
        
        # Audio components
        if TTS_AVAILABLE:
            self.text_processor = TextPostProcessor()
            self.voice = voice()
            print("✅ TTS Module Loaded")
        else:
            self.text_processor = None
            self.voice = None
            print("⚠️ TTS Module Not Available")
        
        if STT_AVAILABLE:
            self.ear = EgyptianEar()
            print("✅ STT Module Loaded")
        else:
            self.ear = None
            print("⚠️ STT Module Not Available")
        
        # Chat sessions storage (per user/session)
        self.chat_sessions: Dict[str, Any] = {}
        
        print("✅ SmartOrchestrator Ready!\n")
    
    def _count_words(self, text: str) -> int:
        """Count words in Arabic or English text."""
        if not text:
            return 0
        # Remove extra whitespace and split
        words = text.strip().split()
        return len(words)
    
    def handle_user_input(self, text: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Rule-Based Routing (The "Traffic Cop")
        
        Logic:
        - Calculate word count
        - If word_count > 10 → Route to Cutter Agent
        - Otherwise (short text/question) → Route to Explanation Agent with RAG
        
        Args:
            text: User input text
            session_id: Session identifier for maintaining context
            
        Returns:
            Dictionary containing the response and metadata
        """
        if not text or not text.strip():
            return {
                "success": False,
                "error": "Empty input text",
                "response": None
            }
        
        # Calculate word count
        word_count = self._count_words(text)
        print(f"📊 Input Analysis: {word_count} words")
        
        try:
            # CONDITION A: Long Text → Cutter Agent
            if word_count > 10:
                print("🔀 Routing to: CUTTER (Text Processing)")
                return self._route_to_cutter(text)
            
            # CONDITION B: Short Text/Question → Explanation Agent with RAG
            else:
                print("🔀 Routing to: EXPLANATION (RAG)")
                return self._route_to_explanation(text, session_id)
                
        except Exception as e:
            print(f"❌ Error in handle_user_input: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    def _route_to_cutter(self, text: str) -> Dict[str, Any]:
        """
        Route to Text Processing Agent (Cutter)
        Returns formatted chunks with titles.
        Also saves output to JSON file for persistence.
        """
        if not CUTTER_AVAILABLE:
            return {
                "success": False,
                "error": "Cutter module not available",
                "response": None
            }
        
        try:
            # Step 1: Split text into semantic chunks
            chunks = split_text_semantically(text)
            
            if not chunks:
                return {
                    "success": False,
                    "error": "No chunks generated from text",
                    "response": None
                }
            
            # Step 2: Generate titles for each chunk
            formatted_chunks = []
            for i, chunk in enumerate(chunks, 1):
                title = generate_title(chunk)
                formatted_chunks.append({
                    "chunk_id": i,
                    "title": title,
                    "content": chunk
                })
            
            print(f"✅ Generated {len(formatted_chunks)} chunks")
            
            # Step 3: Prepare response
            response_data = {
                "success": True,
                "agent": "cutter",
                "word_count": self._count_words(text),
                "num_chunks": len(formatted_chunks),
                "chunks": formatted_chunks,
                "response": formatted_chunks
            }
            
            # Step 4: Save to JSON file
            try:
                # Create outputs directory if it doesn't exist
                outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
                os.makedirs(outputs_dir, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = os.path.join(outputs_dir, f"cutter_output_{timestamp}.json")
                
                # Save to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(response_data, f, ensure_ascii=False, indent=2)
                
                print(f"💾 Output saved to: {output_file}")
                response_data["saved_to"] = output_file
                
            except Exception as save_error:
                print(f"⚠️ Failed to save output to JSON: {save_error}")
                # Don't fail the entire operation if saving fails
            
            return response_data
            
        except Exception as e:
            print(f"❌ Cutter Error: {e}")
            return {
                "success": False,
                "error": f"Cutter processing failed: {str(e)}",
                "response": None
            }
    
    def _route_to_explanation(self, text: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Route to Explanation Agent
        Retrieves RAG context and generates autism-friendly explanation.
        """
        try:
            # Step 1: Retrieve context from ChromaDB
            print("🔍 Retrieving RAG context...")
            context_items = _get_context_impl(
                self.chroma_client,
                text,
                self.embed_model,
                k=3
            )
            
            # Step 2: Prepare context string
            context_str = "\n".join([
                f"- {item.get('original_content', {}).get('autism_friendly_ar', '')}"
                for item in context_items
            ])
            
            print(f"✅ Retrieved {len(context_items)} context items")
            
            # Step 3: Get or create chat session
            if session_id not in self.chat_sessions:
                system_instruction = prepare_system_instruction()
                self.chat_sessions[session_id] = initialize_chat_session(
                    self.gemini_client,
                    system_instruction
                )
                print(f"✨ Created new chat session: {session_id}")
            
            chat_session = self.chat_sessions[session_id]
            
            # Step 4: Generate explanation using RAG
            print("💬 Generating RAG-based explanation...")
            explanation = generate_rag_answer_with_chat(
                chat_session=chat_session,
                query_text=text,
                context_string=context_str,
                is_clarification=False
            )
            
            print("✅ Explanation generated")
            
            return {
                "success": True,
                "message": explanation
            }
            
        except Exception as e:
            print(f"❌ Explanation Error: {e}")
            return {
                "success": False,
                "message": f"حصل خطأ في توليد الشرح: {str(e)}"
            }
    
    # ==========================================
    # STT INTEGRATION (Input)
    # ==========================================
    
    def process_voice_input(self, session_id: str = "default") -> Dict[str, Any]:
        """
        Process voice input using STT module.
        
        Flow:
        1. Call listen() from STT.py
        2. Save transcription to shared_data.json
        3. Pass transcribed text to handle_user_input
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary containing transcription and AI response
        """
        if not STT_AVAILABLE or not self.ear:
            return {
                "success": False,
                "error": "STT module not available",
                "transcription": None,
                "response": None
            }
        
        try:
            print("\n🎤 Starting voice input...")
            
            # Step 1: Listen and transcribe
            transcribed_text = self.ear.listen()
            
            if not transcribed_text or not transcribed_text.strip():
                print("⚠️ No speech detected")
                return {
                    "success": False,
                    "error": "No speech detected",
                    "transcription": None,
                    "response": None
                }
            
            print(f"📝 Transcribed: {transcribed_text}")
            
            # Step 2: Save to shared_data.json
            JsonWriter.save_transcription(transcribed_text)
            
            # Step 3: Process with handle_user_input
            ai_response = self.handle_user_input(transcribed_text, session_id)
            
            return {
                "success": True,
                "transcription": transcribed_text,
                "ai_response": ai_response,
                "response": ai_response.get("response")
            }
            
        except Exception as e:
            print(f"❌ Voice Input Error: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcription": None,
                "response": None
            }
    
    # ==========================================
    # TTS INTEGRATION (Output)
    # ==========================================
    
    def speak_latest_response(self, text_to_speak: str) -> Dict[str, Any]:
        """
        Convert text to speech using TTS module.
        Triggered manually (e.g., when user clicks "Hear" button).
        
        Args:
            text_to_speak: Text to convert to speech
            
        Returns:
            Dictionary containing success status
        """
        if not TTS_AVAILABLE or not self.voice or not self.text_processor:
            return {
                "success": False,
                "error": "TTS module not available"
            }
        
        if not text_to_speak or not text_to_speak.strip():
            return {
                "success": False,
                "error": "No text provided for TTS"
            }
        
        try:
            print(f"\n🔊 Preparing to speak: {text_to_speak[:50]}...")
            
            # Step 1: Normalize text for TTS
            normalized_text = self.text_processor.normalize_for_tts(text_to_speak)
            print(f"✨ Normalized: {normalized_text[:50]}...")
            
            # Step 2: Speak using voice module
            self.voice.speak(normalized_text)
            
            return {
                "success": True,
                "original_text": text_to_speak,
                "normalized_text": normalized_text
            }
            
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==========================================
    # INTERACTIVE LESSON LOOP
    # ==========================================
    
    def run_interactive_lesson(
        self, 
        lesson_id: int, 
        session_id: str,
        user_input: Optional[str] = None,
        use_tts: bool = True,
        use_stt: bool = False
    ) -> Dict[str, Any]:
        """
        Run interactive lesson loop with explanation, TTS, STT, and quiz.
        
        Args:
            lesson_id: ID of the lesson to teach
            session_id: Unique session identifier
            user_input: Optional text input (if not using STT)
            use_tts: Whether to automatically speak responses
            use_stt: Whether to use voice input
            
        Returns:
            Dictionary with current state, message, and next action
        """
        # Initialize session if needed
        session_key = f"interactive_{session_id}"
        if session_key not in self.chat_sessions:
            self.chat_sessions[session_key] = {
                "state": "LOADING",
                "lesson_id": lesson_id,
                "lesson_content": None,
                "context_str": None,
                "current_mcq": None,
                "explanation_attempts": 0,
                "quiz_attempts": 0,          # Track number of questions asked
                "asked_questions": [],       # Track questions to avoid repetition
                "previous_feedback": ""      # Store feedback to say before next question
            }
        
        session = self.chat_sessions[session_key]
        
        try:
            # ==========================================
            # STATE: LOADING - Fetch lesson from database
            # ==========================================
            if session["state"] == "LOADING":
                print(f"📚 Loading lesson {lesson_id}...")
                
                lesson_data = fetch_lesson_by_id(lesson_id)
                if not lesson_data:
                    return {
                        "success": False,
                        "state": "ERROR",
                        "message": "❌ الدرس غير موجود",
                        "needs_input": False
                    }
                
                # Retrieve RAG context
                print("🔍 Retrieving context from database...")
                context_items = _get_context_impl(
                    self.chroma_client,
                    lesson_data["content"],
                    self.embed_model,
                    k=3
                )
                
                context_str = "\n".join([
                    item.get('original_content', {}).get('autism_friendly_ar', '')
                    for item in context_items
                ])
                
                # Update session
                session["lesson_content"] = lesson_data["content"]
                session["context_str"] = context_str
                session["state"] = "EXPLAINING"
                
                print(f"✅ Lesson loaded: {lesson_data['content'][:50]}...")
            
            # ==========================================
            # STATE: EXPLAINING - Generate and speak explanation
            # ==========================================
            if session["state"] == "EXPLAINING":
                print("💬 Generating explanation...")
                
                # Get or create chat session for this lesson
                if session_key not in sessions:
                    system_instruction = prepare_system_instruction()
                    chat_session = initialize_chat_session(
                        self.gemini_client,
                        system_instruction
                    )
                    sessions[session_key] = chat_session
                else:
                    chat_session = sessions[session_key]
                
                # Generate explanation
                is_clarification = session["explanation_attempts"] > 0
                explanation = generate_rag_answer_with_chat(
                    chat_session=chat_session,
                    query_text=session["lesson_content"],
                    context_string=session["context_str"],
                    is_clarification=is_clarification
                )
                
                session["explanation_attempts"] += 1
                
                # Speak explanation if TTS enabled
                audio_played = False
                if use_tts and self.voice:
                    print("🔊 Speaking explanation...")
                    tts_result = self.speak_latest_response(explanation)
                    audio_played = tts_result.get("success", False)
                
                # Move to waiting for confirmation
                session["state"] = "AWAITING_CONFIRMATION"
                
                return {
                    "success": True,
                    "state": "AWAITING_CONFIRMATION",
                    "message": explanation,
                    "audio_played": audio_played,
                    "needs_input": True,
                    "prompt": "😊 فهمت يا بطل؟ (قول 'فهمت' أو 'مش فاهم')"
                }
            
            # ==========================================
            # STATE: AWAITING_CONFIRMATION - Check if student understands
            # ==========================================
            elif session["state"] == "AWAITING_CONFIRMATION":
                # Get input (either from parameter or STT)
                if use_stt and not user_input:
                    print("🎤 Listening for voice input...")
                    voice_result = self.process_voice_input(session_id)
                    if voice_result.get("success"):
                        user_input = voice_result.get("transcription", "")
                    else:
                        return {
                            "success": False,
                            "state": session["state"],
                            "message": "❌ لم أستطع سماع ردك. حاول مرة أخرى.",
                            "needs_input": True
                        }
                
                if not user_input:
                    return {
                        "success": False,
                        "state": session["state"],
                        "message": "⚠️ من فضلك أدخل ردك",
                        "needs_input": True
                    }
                
                user_input_lower = user_input.lower().strip()
                
                # Check for clarification request
                clarification_phrases = ['مش فاهم', 'مش فاهمة', 'تاني', 'اشرحلي تاني', 'ممكن توضيح', 'مفهمتش']
                confirmation_phrases = ['فهمت', 'تمام', 'خلاص', 'شكرا', 'كويس', 'اه', 'نعم']
                
                is_clarification = any(phrase in user_input_lower for phrase in clarification_phrases)
                is_confirmation = any(phrase in user_input_lower for phrase in confirmation_phrases)
                
                if is_clarification:
                    # Go back to explaining (will be simpler this time)
                    session["state"] = "EXPLAINING"
                    return self.run_interactive_lesson(
                        lesson_id=lesson_id,
                        session_id=session_id,
                        user_input=None,
                        use_tts=use_tts,
                        use_stt=False  # Already got input
                    )
                
                elif is_confirmation:
                    # Move to quiz
                    session["state"] = "QUIZ_GENERATING"
                else:
                    return {
                        "success": True,
                        "state": session["state"],
                        "message": "قولّي 'فهمت' لو تمام 👌\nأو 'مش فاهم' لو تحب أشرح تاني 😊",
                        "needs_input": True
                    }
            
            # ==========================================
            # STATE: QUIZ_GENERATING - Create quiz question
            # ==========================================
            if session["state"] == "QUIZ_GENERATING":
                print(f"❓ Generating quiz question (Attempt {session['quiz_attempts'] + 1}/3)...")
                
                # PASS PREVIOUS QUESTIONS TO AVOID REPETITION
                mcq = generate_mcq(
                    self.gemini_client, 
                    session["context_str"],
                    previous_questions=session["asked_questions"]
                )
                
                if not mcq:
                    return {
                        "success": False,
                        "state": "ERROR",
                        "message": "❌ حصل خطأ في توليد السؤال. حاول مرة أخرى.",
                        "needs_input": False
                    }
                
                session["current_mcq"] = mcq
                session["asked_questions"].append(mcq["question_ar"]) # Log this question
                session["state"] = "QUIZ_ANSWERING"
                
                # Format quiz message
                options = "\n".join([
                    f"{i+1}. {opt}" 
                    for i, opt in enumerate(mcq["options_ar"])
                ])
                
                # Check if there is feedback from a previous wrong answer
                intro_text = "✅ شاطر! خد السؤال ده:"
                if session.get("previous_feedback"):
                    intro_text = f"{session['previous_feedback']}\n\nيلا نجرب سؤال تاني يا بطل:"
                    session["previous_feedback"] = "" # Clear it after using

                quiz_message = (
                    f"{intro_text}\n\n"
                    f"❓ {mcq['question_ar']}\n\n"
                    f"{options}\n\n"
                    "اكتب رقم الإجابة (1 أو 2 أو 3)."
                )
                
                # Speak quiz if TTS enabled
                audio_played = False
                if use_tts and self.voice:
                    print("🔊 Speaking quiz...")
                    tts_result = self.speak_latest_response(quiz_message)
                    audio_played = tts_result.get("success", False)
                
                return {
                    "success": True,
                    "state": "QUIZ_ANSWERING",
                    "message": quiz_message,
                    "audio_played": audio_played,
                    "quiz": mcq,
                    "needs_input": True
                }
            
            # ==========================================
            # STATE: QUIZ_ANSWERING - Check answer and provide feedback
            # ==========================================
            elif session["state"] == "QUIZ_ANSWERING":
                # Get input (either from parameter or STT)
                if use_stt and not user_input:
                    print("🎤 Listening for quiz answer...")
                    voice_result = self.process_voice_input(session_id)
                    if voice_result.get("success"):
                        user_input = voice_result.get("transcription", "")
                    else:
                        return {
                            "success": False,
                            "state": session["state"],
                            "message": "❌ لم أستطع سماع ردك. حاول مرة أخرى.",
                            "needs_input": True
                        }
                
                if not user_input:
                    return {
                        "success": False,
                        "state": session["state"],
                        "message": "⚠️ من فضلك أدخل رقم الإجابة",
                        "needs_input": True
                    }
                
                mcq = session["current_mcq"]
                
                # Parse answer
                try:
                    choice_idx = int(user_input.strip()) - 1
                    if choice_idx < 0 or choice_idx >= len(mcq["options_ar"]):
                        raise ValueError("Invalid choice")
                    
                    correct_idx = int(mcq["correct_answer_ar"]) - 1
                    is_correct = choice_idx == correct_idx
                    user_choice_text = mcq["options_ar"][choice_idx]
                    correct_answer_text = mcq["options_ar"][correct_idx]
                    
                    # Extract gentle explanation (fallback if missing)
                    gentle_explanation = mcq.get("gentle_explanation_if_wrong", f"الإجابة الصح هي: {correct_answer_text}")

                except Exception:
                    return {
                        "success": False,
                        "state": session["state"],
                        "message": "⚠️ من فضلك اكتب رقم صحيح (1 أو 2 أو 3)",
                        "needs_input": True
                    }
                
                # Log to database
                log_interaction_db({
                    "timestamp": datetime.datetime.now(),
                    "user_input": user_input,
                    "intent": "Interactive_Lesson_MCQ",
                    "topic": session["lesson_content"],
                    "question": mcq["question_ar"],
                    "correct": is_correct,
                    "correct_answer": correct_answer_text,
                    "user_choice": user_choice_text,
                    "topic_id": lesson_id
                })
                
                # === ADAPTIVE LOOP & PERSISTENT STORAGE LOGIC ===
                
                if is_correct:
                    # Case 1: Answer is Correct -> Finish & Generate Review
                    session["state"] = "COMPLETED"
                    completion_message = "🎉 برافو عليك! إجابة ممتازة! 👏\nانتهى الدرس وتم حفظ أسئلة المراجعة."

                    # --- PHASE 2: GENERATE & SAVE REVIEW QUESTIONS ---
                    print("⚙️ Generating review questions for JSON files...")
                    try:
                        # 1. Generate 4 new questions (avoiding the one just asked)
                        all_review_questions = generate_batch_mcqs(
                            self.gemini_client,
                            session["context_str"],
                            count=4,
                            previous_questions=session["asked_questions"]
                        )
                        
                        if all_review_questions and len(all_review_questions) >= 2:
                            # 2. Split them: 2 for Lesson Review, 2 for Milestone
                            lesson_qs = all_review_questions[:2]
                            milestone_qs = all_review_questions[2:] if len(all_review_questions) > 2 else []
                            
                            # 3. Save to files
                            lesson_title = session.get("lesson_content", "Unknown Lesson")
                            
                            save_questions_to_file("lesson_review.json", lesson_qs, lesson_id, lesson_title)
                            if milestone_qs:
                                save_questions_to_file("milestone_review.json", milestone_qs, lesson_id, lesson_title)
                                
                    except Exception as e:
                        print(f"⚠️ Failed to generate review questions: {e}")
                        # We don't stop the lesson completion if saving fails
                    # ------------------------------------------------
                    
                else:
                    # Case 2: Answer is Wrong -> Check attempts
                    session["quiz_attempts"] += 1
                    
                    if session["quiz_attempts"] < 3:
                        # Retry allowed: Prepare gentle feedback and loop back to GENERATING
                        session["state"] = "QUIZ_GENERATING"
                        session["previous_feedback"] = f"معلش، حاول تاني! {gentle_explanation}"
                        
                        # Recursive call to immediately generate the next question
                        return self.run_interactive_lesson(
                            lesson_id, session_id, user_input=None, use_tts=use_tts, use_stt=False
                        )
                    else:
                        # Max attempts reached -> Finish
                        session["state"] = "COMPLETED"
                        completion_message = f"مش مشكلة! {gentle_explanation}\nلقد بذلت مجهود رائع اليوم! 🌟"
                
                # Speak feedback if TTS enabled
                audio_played = False
                if use_tts and self.voice:
                    print("🔊 Speaking feedback...")
                    tts_result = self.speak_latest_response(completion_message)
                    audio_played = tts_result.get("success", False)
                
                # Clean up session
                if session["state"] == "COMPLETED":
                    del self.chat_sessions[session_key]
                    if session_key in sessions:
                        del sessions[session_key]
                
                return {
                    "success": True,
                    "state": "COMPLETED",
                    "message": completion_message,
                    "audio_played": audio_played,
                    "is_correct": is_correct,
                    "needs_input": False
                }
            
            # Fallback
            return {
                "success": False,
                "state": "ERROR",
                "message": f"❌ حالة غير معروفة: {session['state']}",
                "needs_input": False
            }
            
        except Exception as e:
            print(f"❌ Interactive Lesson Error: {e}")
            return {
                "success": False,
                "state": "ERROR",
                "message": f"❌ حصل خطأ: {str(e)}",
                "needs_input": False
            }


# ==========================================
# INITIALIZE ORCHESTRATOR
# ==========================================

# Global orchestrator instance
orchestrator = SmartOrchestrator()

# ==========================================
# DATABASE HELPERS
# ==========================================

def get_db_connection():
    """Get PostgreSQL database connection."""
    db_url = os.getenv("DATABASE_URL")
    assert db_url, "DATABASE_URL is not set"

    if db_url.startswith("postgresql+psycopg://"):
        db_url = db_url.replace("postgresql+psycopg://", "postgresql://")

    return psycopg2.connect(db_url)


def fetch_lesson_by_id(lesson_id):
    """Fetch lesson by lesson_id."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title || ': ' || description AS content
            FROM lessons
            WHERE id = %s;
        """, (lesson_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return {"id": row[0], "content": row[1]}
        return None
    except Exception as e:
        print(f"❌ DB Error: {e}")
        return None


def log_interaction_db(data):
    """Log interaction to database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO log_table 
            (timestamp, user_input, intent, topic, question, correct, correct_answer, user_choice, topic_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get("timestamp"), data.get("user_input"), data.get("intent"),
            data.get("topic"), data.get("question"), data.get("correct"), 
            data.get("correct_answer"), data.get("user_choice"), data.get("topic_id")
        )
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ DB Log Error: {e}")


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================

def process_text_input(text: str, session_id: str = "default") -> Dict[str, Any]:
    """
    Convenience function to process text input via orchestrator.
    
    Args:
        text: User input text
        session_id: Session identifier
        
    Returns:
        AI response dictionary
    """
    return orchestrator.handle_user_input(text, session_id)


def process_voice_input(session_id: str = "default") -> Dict[str, Any]:
    """
    Convenience function to process voice input.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dictionary with transcription and AI response
    """
    return orchestrator.process_voice_input(session_id)


def speak_text(text: str) -> Dict[str, Any]:
    """
    Convenience function to speak text.
    
    Args:
        text: Text to speak
        
    Returns:
        Success status dictionary
    """
    return orchestrator.speak_latest_response(text)


# ==========================================
# BACKWARD COMPATIBILITY FUNCTIONS
# (For existing ai_router.py imports)
# ==========================================

def get_context_from_db(query_text: str, k: int = 3) -> List[Dict]:
    """
    Get context from ChromaDB (legacy function for backward compatibility).
    
    Args:
        query_text: Query to search for
        k: Number of results to retrieve
        
    Returns:
        List of context items
    """
    try:
        return _get_context_impl(chroma_client, query_text, embed_model, k=k)
    except Exception as e:
        print(f"⚠️ get_context_from_db error: {e}")
        return []


def generate_explanation(topic: str, context_items: List[Dict], is_clarification: bool = False) -> str:
    """
    Generate explanation using Gemini (legacy function for backward compatibility).
    
    Args:
        topic: Topic to explain
        context_items: Context from RAG
        is_clarification: Whether this is a clarification request
        
    Returns:
        Generated explanation text
    """
    try:
        # Use the orchestrator's explanation routing
        result = orchestrator._route_to_explanation(topic, session_id="legacy")
        return result.get("response", "حصل خطأ في توليد الشرح")
    except Exception as e:
        print(f"⚠️ generate_explanation error: {e}")
        return f"حصل خطأ: {str(e)}"


def generate_mcq_ai(context_str: str) -> Optional[Dict]:
    """
    Generate MCQ question (legacy function for backward compatibility).
    
    Args:
        context_str: Context string for question generation
        
    Returns:
        MCQ dictionary or None
    """
    try:
        return generate_mcq(gemini_client, context_str)
    except Exception as e:
        print(f"⚠️ generate_mcq_ai error: {e}")
        return None


def generate_feedback(question: str, correct_opt: str, user_choice: str, is_correct: bool) -> str:
    """
    Generate feedback for MCQ answer (legacy function for backward compatibility).
    
    Args:
        question: The MCQ question
        correct_opt: Correct answer option
        user_choice: User's choice
        is_correct: Whether user was correct
        
    Returns:
        Feedback text
    """
    prompt = f"""
    السؤال: {question}
    الجواب الصحيح: {correct_opt}
    جواب الطفل: {user_choice} ({'صح' if is_correct else 'غلط'})
    أعط رد فعل قصير ومشجع باللهجة المصرية.
    """
    
    try:
        response = gemini_client.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"⚠️ generate_feedback error: {e}")
        if is_correct:
            return "👏 برافو! إجابة صح"
        else:
            return f"😊 مش مشكلة، الإجابة الصحيحة كانت: {correct_opt}"


# Constants for backward compatibility
CLARIFICATION_PHRASES = ['مش فاهم', 'مش فاهمة', 'تاني', 'اشرحلي تاني', 'ممكن توضيح','يعني ايه']
CONFIRMATION_PHRASES = ['فهمت', 'تمام', 'خلاص', 'شكرا', 'كويس']