import os
import json
import torch
import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from google import genai
import psycopg2
from typing import Dict, Any
import datetime

load_dotenv()

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_DB_PATH = "../../ai_rag_db"
COLLECTION_NAME = "autism_content_arabic"
EMBEDDING_MODEL_NAME = 'intfloat/multilingual-e5-large'
GENERATION_MODEL = 'gemini-2.5-flash'

# --- AI / RAG ---
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
device = "cuda" if torch.cuda.is_available() else "cpu"
embed_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)

# --- Session Storage ---
sessions: Dict[str, Dict[str, Any]] = {}

# --- Constants ---
CLARIFICATION_PHRASES = ['مش فاهم', 'مش فاهمة', 'تاني', 'اشرحلي تاني', 'ممكن توضيح']
CONFIRMATION_PHRASES = ['فهمت', 'تمام', 'خلاص', 'شكرا', 'كويس']

# --- DB helpers ---
def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    assert db_url, "DATABASE_URL is not set"

    if db_url.startswith("postgresql+psycopg://"):
        db_url = db_url.replace("postgresql+psycopg://", "postgresql://")

    return psycopg2.connect(db_url)

def fetch_lesson_by_id(lesson_id):
    """Fetch lesson by lesson_id instead of fetching next lesson."""
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

# --- AI helpers ---
def get_context_from_db(query_text, k=3):
    try:
        collection = chroma_client.get_collection(COLLECTION_NAME)
        query_vector = embed_model.encode([f"query: {query_text}"], normalize_embeddings=True)[0].tolist()
        results = collection.query(query_embeddings=[query_vector], n_results=k, include=['documents', 'metadatas'])
        context = []
        if results and results.get('documents') and results['documents'][0]:
            for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                context.append({"original_content": meta})
        return context
    except Exception as e:
        print(f"❌ Retrieval Error: {e}")
        return []

def generate_explanation(topic, context_items, is_clarification=False):
    context_str = "\n".join([f"- {item['original_content'].get('autism_friendly_ar', '')}" for item in context_items])
    if is_clarification:
        prompt = f"""
        الطفل قال: "مش فاهم".
        الموضوع: {topic}
        اشرح له مرة أخرى بطريقة مختلفة تماماً وأبسط. استخدم مثالاً جديداً.
        معلومات مرجعية: {context_str}
        """
    else:
        prompt = f"""
        الموضوع الجديد هو: {topic}
        اشرح هذا الموضوع لطفل متوحد بلهجة مصرية بسيطة جداً ومباشرة.
        استخدم المعلومات التالية: {context_str}
        """
    response = gemini_client.models.generate_content(model=GENERATION_MODEL, contents=[prompt])
    return response.text

def generate_mcq_ai(context_str):
    prompt = f"""
    بناءً على هذا النص: "{context_str}"
    أنشئ سؤال MCQ واحد للأطفال.
    Output JSON format: {{ "question_ar": "...", "correct_answer_ar": "1", "options_ar": ["opt1", "opt2", "opt3"] }}
    """
    try:
        response = gemini_client.models.generate_content(model=GENERATION_MODEL, contents=[prompt])
        text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(text)
    except:
        return None

def generate_feedback(question, correct_opt, user_choice, is_correct):
    prompt = f"""
    السؤال: {question}
    الجواب الصحيح: {correct_opt}
    جواب الطفل: {user_choice} ({'صح' if is_correct else 'غلط'})
    أعط رد فعل قصير ومشجع باللهجة المصرية.
    """
    response = gemini_client.models.generate_content(model=GENERATION_MODEL, contents=[prompt])
    return response.text
