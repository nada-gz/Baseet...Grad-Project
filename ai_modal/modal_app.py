"""
Baseet AI Modal Service - Complete AI Services
Includes: RAG, Text Splitting, TTS, STT, Lesson Orchestration
"""

import modal
import os
import json
from typing import Optional, Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel
import datetime

# ============================================
# MODAL APP CONFIGURATION
# ============================================

app = modal.App("baseet-ai")


image = modal.Image.debian_slim(python_version="3.11").pip_install(
    # Web Framework
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    
    # Core AI/ML
    "google-genai>=1.0.0",
    "chromadb>=0.4.0",
    "sentence-transformers>=2.2.0",
    
    # Deep Learning
    "torch>=2.0.0",
    "transformers>=4.30.0",
    "librosa>=0.10.0",
    
    # Audio
    "elevenlabs>=1.0.0",
    "sounddevice>=0.4.6",
    "scipy>=1.10.0",
    
    # NLP & Text
    "scikit-learn>=1.3.0",
    "arabic-reshaper>=3.0.0",
    "python-bidi>=0.4.2",
    
    # Database
    "psycopg2-binary>=2.9.0",
    
    # Document Processing
    "pytesseract>=0.3.10",
    "Pillow>=10.0.0",
    "PyMuPDF>=1.23.0",
    
    # Utilities
    "python-dotenv>=1.0.0",
    "colorama>=0.4.6",
    "numpy>=1.24.0",
    "pydantic>=2.0.0",
)

# ============================================
# PYDANTIC MODELS
# ============================================

class ExplainRequest(BaseModel):
    text: str
    lesson_id: Optional[int] = None
    session_id: Optional[str] = None
    is_clarification: bool = False

class CutterRequest(BaseModel):
    text: str
    threshold: float = 0.35

class TTSRequest(BaseModel):
    text: str
    use_postprocessing: bool = True

class STTRequest(BaseModel):
    audio_base64: str
    duration_seconds: int = 7

class LessonStartRequest(BaseModel):
    lesson_id: int
    student_id: int

class LessonChatRequest(BaseModel):
    lesson_id: int
    student_id: int
    message: str

class BotResponse(BaseModel):
    message: str
    state: str
    progress: Optional[int] = 0

# ============================================
# MODAL FUNCTION - ALL SERVICES
# ============================================

rag_volume = modal.Volume.from_name(
    "baseet-rag-storage",
    create_if_missing=True
)
@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("baseet-ai-secrets"),
    ],
    memory=4096,
    gpu="any",
    volumes={"/data": rag_volume},
)
@modal.asgi_app()
def fastapi_app():
    from google import genai
    import torch
    import chromadb
    from sentence_transformers import SentenceTransformer
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api = FastAPI(title="Baseet AI Service")
    
    # ============================================
    # INITIALIZATION
    # ============================================
    
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
    
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY not configured")
    
    # Initialize AI components
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    chroma_client = chromadb.PersistentClient(
        path="/data/chroma"
    )
    collection = chroma_client.get_or_create_collection(
        name="baseet-lessons"
    )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    embed_model = SentenceTransformer('intfloat/multilingual-e5-large', device=device)
    
    # Session storage
    sessions: Dict[str, Dict[str, Any]] = {}
    
    # ============================================
    # HELPER FUNCTIONS
    # ============================================
    
    def get_context_from_chroma(query_text: str, k: int = 3):
        """Fetch context from ChromaDB for RAG"""
        try:
            query_vector = embed_model.encode([f"query: {query_text}"], normalize_embeddings=True)[0].tolist()
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=k,
                include=['documents', 'metadatas']
            )
            
            context = []
            if results and results.get('documents') and results['documents'][0]:
                for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                    context.append({"text": doc, "metadata": meta})
            return context
        except Exception as e:
            print(f"❌ ChromaDB Error: {e}")
            return []
    
    def normalize_arabic(text: str) -> str:
        """Normalize Arabic text"""
        import re
        text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
        text = re.sub(r'[أإآ]', 'ا', text)
        text = re.sub(r'ـ', '', text)
        return text
    
    # ============================================
    # ENDPOINTS - HEALTH & INFO
    # ============================================
    
    @api.get("/health")
    def health():
        return {
            "status": "ok",
            "service": "modal-ai",
            "device": device,
            "services": {
                "gemini": "✅" if GEMINI_API_KEY else "❌",
                "chromadb": "✅",
                "embeddings": "✅",
                "cuda": "✅" if device == "cuda" else "❌"
            }
        }
    
    @api.get("/")
    def root():
        return {"message": "Baseet AI service is running"}
    
    # ============================================
    # ENDPOINTS - INGESTION (RAG)
    # ============================================
    
    @api.post("/ai/ingest")
    def ingest(payload: dict):
        texts = payload.get("texts", [])
        metadatas = payload.get("metadatas", [{}] * len(texts))
    
        if not texts:
            return {"error": "No texts provided"}
    
        embeddings = embed_model.encode(
            [f"passage: {t}" for t in texts],
            normalize_embeddings=True
        ).tolist()
    
        ids = [f"doc_{i}_{datetime.datetime.now().timestamp()}" for i in range(len(texts))]
    
        collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )
    
        return {"status": "ingested", "count": len(texts)}
    
    # ============================================
    # ENDPOINTS - EXPLANATION & RAG
    # ============================================
    
    @api.post("/ai/explain")
    async def explain(payload: ExplainRequest):
        """Generate explanation using Gemini + RAG context"""
        try:
            # Get context from ChromaDB
            context_items = get_context_from_chroma(payload.text, k=3)
            context_str = "\n".join([f"- {item['text']}" for item in context_items]) if context_items else "No context available"
            
            # Prepare prompt
            intent_instruction = (
                "**نية الطفل (Intent):** طلب توضيح/إعادة شرح" if payload.is_clarification
                else "**نية الطفل (Intent):** سؤال جديد"
            )
            
            prompt = f"""
أنت مساعد تعليمي للأطفال.

❗ القاعدة الصارمة:
- استخدم فقط المعلومات الموجودة في السياق.
- إذا لم تجد الإجابة في السياق، قل: "لا أعرف من الدرس".

السياق:
{context_str}

السؤال:
{payload.text}
"""
            
            # Generate response
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt],
            )
            
            return {
                "answer": response.text,
                "context_used": len(context_items) > 0,
                "context_items": len(context_items)
            }
        except Exception as e:
            return {"error": f"Explanation failed: {str(e)}"}, 500
    
    # ============================================
    # ENDPOINTS - TEXT SPLITTING/CUTTER
    # ============================================
    
    @api.post("/ai/split-text")
    async def split_text(payload: CutterRequest):
        """Split text semantically using embeddings"""
        try:
            import re
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Split by sentences
            sentences = re.split(r'[.؟!]+', payload.text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return {"error": "No valid sentences found"}, 400
            
            # Encode and split
            norm_sentences = [normalize_arabic(s) for s in sentences]
            embeddings = embed_model.encode(norm_sentences)
            
            chunks = []
            current_chunk = [sentences[0]]
            
            for i in range(len(sentences) - 1):
                score = cosine_similarity([embeddings[i]], [embeddings[i+1]])[0][0]
                if score >= payload.threshold:
                    current_chunk.append(sentences[i+1])
                else:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [sentences[i+1]]
            
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            
            return {
                "success": True,
                "chunks_count": len(chunks),
                "chunks": [{"id": i+1, "text": chunk} for i, chunk in enumerate(chunks)]
            }
        except Exception as e:
            return {"error": f"Text splitting failed: {str(e)}"}, 500
    
    # ============================================
    # ENDPOINTS - TEXT-TO-SPEECH (TTS)
    # ============================================
    
    @api.post("/ai/tts")
    async def tts(payload: TTSRequest):
        """Convert text to speech using ElevenLabs"""
        try:
            if not ELEVENLABS_API_KEY:
                return {"error": "ELEVENLABS_API_KEY not configured"}, 500
            
            from elevenlabs.client import ElevenLabs
            from elevenlabs import VoiceSettings
            import base64
            
            client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
            voice_id = os.environ.get("VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
            
            audio = client.text_to_speech.convert(
                text=payload.text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75),
            )
            
            audio_bytes = b"".join(audio)
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            
            return {
                "success": True,
                "audio_base64": audio_base64,
                "text": payload.text
            }
        except Exception as e:
            return {"error": f"TTS failed: {str(e)}"}, 500
    
    # ============================================
    # ENDPOINTS - SPEECH-TO-TEXT (STT)
    # ============================================
    
    @api.post("/ai/stt")
    async def stt(payload: STTRequest):
        """Convert speech to text using Wav2Vec2 Egyptian Arabic"""
        try:
            from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
            import base64
            import numpy as np
            import librosa
            
            model_id = "IbrahimAmin/egyptian-arabic-wav2vec2-xlsr-53"
            processor = Wav2Vec2Processor.from_pretrained(model_id)
            model = Wav2Vec2ForCTC.from_pretrained(model_id)
            model.to(device)
            
            audio_bytes = base64.b64decode(payload.audio_base64)
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            audio_resampled = librosa.resample(audio_array, orig_sr=16000, target_sr=16000)
            
            inputs = processor(audio_resampled, sampling_rate=16000, return_tensors="pt", padding=True)
            
            with torch.no_grad():
                logits = model(inputs.input_values.to(device)).logits
            
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = processor.batch_decode(predicted_ids)[0]
            
            return {
                "success": True,
                "transcription": transcription
            }
        except Exception as e:
            return {"error": f"STT failed: {str(e)}"}, 500
    
    # ============================================
    # ENDPOINTS - LESSON ORCHESTRATION
    # ============================================
    
    @api.post("/ai/lesson/start", response_model=BotResponse)
    async def start_lesson(request: LessonStartRequest):
        """Start an interactive lesson"""
        try:
            session_id = f"student_{request.student_id}_lesson_{request.lesson_id}"
            sessions[session_id] = {
                "lesson_id": request.lesson_id,
                "student_id": request.student_id,
                "state": "STARTED",
                "progress": 0,
                "created_at": datetime.datetime.now().isoformat()
            }
            
            message = f"مرحباً! 👋 هيا بنا نتعلم عن الدرس رقم {request.lesson_id}"
            return BotResponse(message=message, state="STARTED", progress=0)
        except Exception as e:
            return BotResponse(message=f"Error: {str(e)}", state="ERROR", progress=0), 500
    
    @api.post("/ai/lesson/chat", response_model=BotResponse)
    async def chat_lesson(request: LessonChatRequest):
        """Chat with AI during lesson"""
        try:
            session_id = f"student_{request.student_id}_lesson_{request.lesson_id}"
            payload = ExplainRequest(text=request.message, lesson_id=request.lesson_id, session_id=session_id)
            response = await explain(payload)
            
            if "error" in response:
                return BotResponse(message="عذراً، حدثت مشكلة. حاول مرة أخرى", state="ERROR", progress=0), 500
            
            if session_id in sessions:
                sessions[session_id]["progress"] = min(100, sessions[session_id].get("progress", 0) + 10)
            
            return BotResponse(
                message=response.get("answer", "No response"),
                state="ACTIVE",
                progress=sessions.get(session_id, {}).get("progress", 0)
            )
        except Exception as e:
            return BotResponse(message=f"Error: {str(e)}", state="ERROR", progress=0), 500
    
    @api.get("/ai/sessions")
    async def get_sessions():
        """Get all active sessions"""
        return {"sessions": len(sessions), "details": sessions}
    
    return api
