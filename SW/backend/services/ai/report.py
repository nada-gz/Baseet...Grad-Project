import os
import textwrap
import psycopg2
from google import genai
from collections import defaultdict
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --- 1. Load Environment Variables ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ Error: GEMINI_API_KEY not found. Check .env file.")

# --- 2. Configuration ---
GENERATION_MODEL = 'gemini-2.5-flash'

# --- 3. Initialize FastAPI App & Gemini Client ---
app = FastAPI(title="Autism Reporting Agent")
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# --- 4. Pydantic Models ---
class ReportResponse(BaseModel):
    report_content: str

# --- 5. Database Functions ---
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def fetch_logs_from_db():
    """Fetch all relevant log entries from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT user_input, intent, topic, question, correct, correct_answer, user_choice 
            FROM log_table
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        logs = [
            {
                "user_input": row[0],
                "intent": row[1],
                "topic": row[2],
                "question": row[3],
                "correct": row[4],
                "correct_answer": row[5],
                "user_choice": row[6]
            } for row in rows
        ]
        cursor.close()
        conn.close()
        return logs
    except Exception as e:
        print(f"❌ DB Fetch Error: {e}")
        return []

def save_report_to_db(report_content):
    """Save the generated report to the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO reports_table (report_text) VALUES (%s)"
        cursor.execute(query, (report_content,))
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Report successfully saved to database!")
        return True
    except Exception as e:
        print(f"❌ DB Save Error: {e}")
        return False

# --- 6. Core Analysis Functions ---
def analyze_session_data(log_data):
    """Analyze raw log data to extract performance statistics."""
    stats = {
        'total_topics': 0,
        'topics_covered': set(),
        'mcq_total': 0,
        'mcq_correct': 0,
        'mcq_incorrect': 0,
        'clarification_count': 0,
        'struggled_topics': defaultdict(lambda: {'clarifications': 0, 'incorrect_mcqs': 0, 'questions': []})
    }

    for entry in log_data:
        topic = entry.get('topic', 'Unknown Topic')
        if entry['intent'] == 'New_Topic':
            if topic not in stats['topics_covered']:
                stats['topics_covered'].add(topic)
                stats['total_topics'] += 1
        elif entry['intent'] == 'Clarification_Request':
            stats['clarification_count'] += 1
            stats['struggled_topics'][topic]['clarifications'] += 1
        elif entry['intent'] == 'MCQ_Attempt':
            stats['mcq_total'] += 1
            stats['struggled_topics'][topic]['questions'].append(entry['question'])
            if entry['correct']:
                stats['mcq_correct'] += 1
            else:
                stats['mcq_incorrect'] += 1
                stats['struggled_topics'][topic]['incorrect_mcqs'] += 1

    # Filter out topics with no struggles
    stats['struggled_topics'] = {
        k: v for k, v in stats['struggled_topics'].items()
        if v['clarifications'] > 0 or v['incorrect_mcqs'] > 0
    }

    return stats

def generate_report_logic(stats, client):
    """Generate a professional report using Gemini based on the statistics."""
    mcq_success_rate = (stats['mcq_correct'] / stats['mcq_total'] * 100) if stats['mcq_total'] > 0 else 0

    struggle_summary = []
    for topic, data in stats['struggled_topics'].items():
        struggle_summary.append(f"- الموضوع: {topic}")
        if data['clarifications'] > 0:
            struggle_summary.append(f"  - طلب توضيح: {data['clarifications']} مرة.")
        if data['incorrect_mcqs'] > 0:
            struggle_summary.append(f"  - إجابات خاطئة: {data['incorrect_mcqs']} أسئلة.")

    struggle_str = "\n".join(struggle_summary) if struggle_summary else "لم يتم تسجيل صعوبات واضحة في الفهم أو الأسئلة."

    system_instruction = textwrap.dedent("""
        أنت مساعد متخصص في تحليل سجلات تفاعل الأطفال ذوي طيف التوحد (Autistic children) وتقديم تقارير احترافية وموجزة.
        **مهمتك:** بناءً على 'ملخص بيانات الأداء'، قم بإنشاء تقرير موجه إلى ولي الأمر أو المعلم أو الطبيب.
        **قواعد كتابة التقرير:**
        1. يجب أن يكون التقرير باللهجة المصرية، بأسلوب بسيط، مشجع وواضح.
        2. يجب أن يركز التقرير على نقاط القوة ونقاط الضعف والمتابعة المقترحة.
        3. يجب أن يبدأ التقرير مباشرة دون مقدمات أو تحيات.
        4. الهيكل: 
           - ملخص الأداء العام
           - نقاط القوة
           - نقاط الضعف والتحديات
           - توصيات للمتابعة
    """)

    prompt = textwrap.dedent(f"""
        **ملخص بيانات الأداء:**
        - إجمالي الموضوعات التي تم تناولها: {stats['total_topics']} موضوع.
        - إجمالي أسئلة الاختيار من متعدد (MCQ): {stats['mcq_total']} سؤال.
        - إجمالي الإجابات الصحيحة: {stats['mcq_correct']} إجابة.
        - إجمالي الإجابات الخاطئة: {stats['mcq_incorrect']} إجابة.
        - نسبة النجاح في أسئلة الـ MCQ: {mcq_success_rate:.2f}%.
        - إجمالي طلبات التوضيح: {stats['clarification_count']} مرة.

        **تفاصيل الموضوعات الصعبة/نقص الفهم:**
        {struggle_str}

        ---
        الآن، قم بتوليد التقرير وفقاً للقواعد أعلاه:
    """)

    try:
        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=[prompt],
            config=dict(system_instruction=system_instruction)
        )
        return response.text
    except Exception as e:
        return f"❌ خطأ في توليد التقرير من Gemini: {e}"

