import os
import json
import chromadb
from google import genai
from sentence_transformers import SentenceTransformer
import torch
import textwrap
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "autism_rag_db")  # Full path to local autism_rag_db
COLLECTION_NAME = "autism_content_arabic"
EMBEDDING_MODEL_NAME = 'intfloat/multilingual-e5-large'
GENERATION_MODEL = 'gemini-2.5-flash'


def setup_retrieval_model():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    query_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)
    return query_model


def get_context_from_db(chroma_client, query_text, embed_model, k=3):
    """Fetches top-k context documents from ChromaDB for the given query."""
    try:
        collection = chroma_client.get_collection(COLLECTION_NAME)
    except Exception as e:
        return []

    query_vector = embed_model.encode([f"query: {query_text}"], normalize_embeddings=True)[0].tolist()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=k,
        include=['documents', 'metadatas', 'distances']
    )

    context = []
    if results and results.get('documents') and results['documents'][0]:
        for doc, meta, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
            context.append({
                "text_to_embed": doc,
                "original_content": meta,
                "distance": dist
            })
    return context


def initialize_chat_session(client, system_instruction):
    """Initializes a persistent chat session with Gemini."""
    chat = client.chats.create(
        model=GENERATION_MODEL,
        config=dict(system_instruction=system_instruction)
    )
    return chat


def generate_rag_answer_with_chat(chat_session, query_text, context_string, is_clarification=False):
    """Sends query + RAG context to the chat session."""
    if is_clarification:
        intent_instruction = (
            "**نية الطفل (Intent):** طلب توضيح/إعادة شرح ('مش فاهم').\n"
            "**تعليمات خاصة:** يجب عليك الآن تغيير طريقة الشرح بالكامل لنفس الموضوع، باستخدام تشبيه جديد أو مثال يومي مختلف. لا تكرر إجابتك السابقة أبداً، ولكن التزم بالسياق المرجعي. ركز على التبسيط الشديد."
        )
    else:
        intent_instruction = (
            "**نية الطفل (Intent):** سؤال جديد/موضوع جديد.\n"
            "**تعليمات خاصة:** **استخدم جميع** المعلومات المتوفرة في 'البيانات المرجعية' لتقديم شرح **كامل وواضح ومبسط** للطفل. لا تكتفِ بجملة واحدة. الشرح يجب أن يكون ودوداً ومركزاً على نقل المعرفة الأساسية."
        )

    prompt = (
        f"{intent_instruction}\n\n"
        f"**البيانات المرجعية (Context):**\n"
        f"```\n{context_string if context_string else 'لا توجد بيانات مرجعية جديدة متوفرة. اعتمد على سياق المحادثة وتوجيهاتك السابقة.'}\n```\n\n"
        f"**استعلام الطفل:** {query_text}"
    )

    try:
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        return f"❌ حصل خطأ أثناء محاولة توليد الإجابة من Gemini. (Error during generation): {e}"


def generate_mcq(client, context_string):
    """Generates one MCQ in Egyptian Arabic based on provided context."""
    output_format_description = """
        The output MUST be a JSON object with the following structure:
        {
          "question_ar": "The MCQ question in simple Egyptian Arabic.",
          "correct_answer_ar": "The correct answer option (e.g., '1' or '2' or '3').",
          "options_ar": [
            "Option 1 in Egyptian Arabic",
            "Option 2 in Egyptian Arabic",
            "Option 3 in Egyptian Arabic"
          ]
        }
    """

    prompt = textwrap.dedent(f"""
        بناءً على المعلومات الموجودة في "البيانات المرجعية"، قم بتوليد سؤال اختيار من متعدد (MCQ) واحد فقط.
        **قواعد توليد السؤال:**
        1. يجب أن يكون السؤال بسيطًا جدًا ومناسبًا لطفل على طيف التوحد (Autistic child).
        2. الإجابة الصحيحة يجب أن تكون مباشرة من "البيانات المرجعية".
        3. يجب أن تحتوي قائمة الخيارات على 3 خيارات (إجابة صحيحة واثنان خاطئان).
        4. يجب أن تكون الخيارات والسؤال بلهجة مصرية عامية بسيطة.

        **البيانات المرجعية (Context):**
        ```
        {context_string}
        ```
        
        {output_format_description}
    """)

    try:
        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=[prompt]
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[len("```json"):]
            if text.endswith("```"):
                text = text[:-len("```")]
        return json.loads(text.strip())
    except Exception as e:
        print(f"❌ خطأ في توليد السؤال أو تحليل JSON: {e}")
        return None


# --- Backend-ready Utilities (No CLI / No local JSONL logging) ---
def prepare_system_instruction():
    """Returns the default system instruction for initializing a chat session."""
    return textwrap.dedent("""
        أنت مساعد تعليمي متخصص في شرح المحتوى العلمي بلهجة مصرية بسيطة جدًا ومناسبة للأطفال ذوي طيف التوحد (Autistic children).
        يجب أن تكون إجابتك مباشرة، وودودة، وبلهجة عامية مصرية (Egyptian Colloquial Arabic).
        
        **قواعد التفاعل:**
        1. **الرد الأولي/موضوع جديد:** استخدم المعلومات المتوفرة في 'البيانات المرجعية' لتقديم إجابتك. يجب أن تكون الإجابة قصيرة، إيجابية، ومركزة.
        2. **التعامل مع 'مش فاهم' (Clarification):** إذا قال الطفل عبارة تدل على عدم الفهم، **يجب عليك تغيير طريقة الشرح** بالكامل لنفس الموضوع الذي تم شرحه سابقاً.
            - استخدم تشبيهاً مختلفاً أو مثالاً يومياً لم يتم ذكره سابقاً.
            - يمكنك استخدام طريقة "سؤال وجواب" بسيطة لتبسيط المفهوم.
            - **لا تكرر الإجابة السابقة أبداً.**
        3. **اللغة:** صيغ الإجابة لتكون بلهجة مصرية عامية (ECA).
    """)

# ==========================================
# 5. GEMINI AGENT TOOLS (for agentic architecture)
# ==========================================

# Define Gemini function calling tools for Explanation Agent
EXPLANATION_TOOLS = [
    {
        "function_declarations": [
            {
                "name": "retrieve_context",
                "description": "Retrieves relevant context from the ChromaDB knowledge base for a given query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The query text to search for in the knowledge base"
                        },
                        "k": {
                            "type": "integer",
                            "description": "Number of top results to retrieve (default: 3)",
                            "default": 3
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "generate_mcq_question",
                "description": "Generates a multiple choice question (MCQ) in Egyptian Arabic based on provided context",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "context": {
                            "type": "string",
                            "description": "The context/content to base the MCQ on"
                        }
                    },
                    "required": ["context"]
                }
            },
            {
                "name": "create_chat_session",
                "description": "Initializes a new Gemini chat session with system instructions for autism-friendly explanations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "system_instruction": {
                            "type": "string",
                            "description": "Optional custom system instruction (uses default if not provided)"
                        }
                    }
                }
            },
            {
                "name": "generate_explanation",
                "description": "Generates an autism-friendly explanation using RAG context",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The query or topic to explain"
                        },
                        "context": {
                            "type": "string",
                            "description": "Retrieved context to use for explanation"
                        },
                        "is_clarification": {
                            "type": "boolean",
                            "description": "Whether this is a clarification request",
                            "default": False
                        }
                    },
                    "required": ["query", "context"]
                }
            }
        ]
    }
]

def execute_explanation_tool(tool_name, args, chroma_client=None, embed_model=None, gemini_client=None):
    """
    Execute an explanation tool based on Gemini function call
    
    Args:
        tool_name: Name of the tool to execute
        args: Dictionary of arguments for the tool
        chroma_client: ChromaDB client (required for retrieve_context)
        embed_model: Embedding model (required for retrieve_context)
        gemini_client: Gemini client (required for other tools)
    
    Returns:
        Tool execution result
    """
    try:
        if tool_name == "retrieve_context":
            if not chroma_client or not embed_model:
                return {"error": "ChromaDB client and embed model required", "success": False}
            
            query = args.get("query", "")
            k = args.get("k", 3)
            context = get_context_from_db(chroma_client, query, embed_model, k=k)
            return {
                "context": context,
                "num_results": len(context),
                "success": True
            }
        
        elif tool_name == "generate_mcq_question":
            if not gemini_client:
                return {"error": "Gemini client required", "success": False}
            
            context = args.get("context", "")
            mcq = generate_mcq(gemini_client, context)
            if mcq:
                return {"mcq": mcq, "success": True}
            else:
                return {"error": "Failed to generate MCQ", "success": False}
        
        elif tool_name == "create_chat_session":
            if not gemini_client:
                return {"error": "Gemini client required", "success": False}
            
            system_instruction = args.get("system_instruction") or prepare_system_instruction()
            chat = initialize_chat_session(gemini_client, system_instruction)
            return {"chat_id": id(chat), "success": True, "chat_session": chat}
        
        elif tool_name == "generate_explanation":
            query = args.get("query", "")
            context = args.get("context", "")
            is_clarification = args.get("is_clarification", False)
            
            # For now, return the context-based explanation structure
            # In full implementation, this would use chat session
            return {
                "query": query,
                "context_provided": bool(context),
                "is_clarification": is_clarification,
                "success": True
            }
        
        else:
            return {"error": f"Unknown tool: {tool_name}", "success": False}
    
    except Exception as e:
        return {"error": str(e), "success": False}

