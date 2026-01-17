import re
import json
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# ==========================================
# 1. SETUP & LOADING
# ==========================================
import os
PATH_SPLITTER = os.path.join(os.path.dirname(__file__), "splitter_model")
PATH_LABELER  = os.path.join(os.path.dirname(__file__), "arat5_model")

print("⏳ Loading Models...")

# Load Splitter
if not os.path.exists(PATH_SPLITTER):
    raise ValueError(f"❌ Error: {PATH_SPLITTER} not found.")
embedder = SentenceTransformer(PATH_SPLITTER)

# Load Labeler
if not os.path.exists(PATH_LABELER):
    raise ValueError(f"❌ Error: {PATH_LABELER} not found.")
tokenizer = AutoTokenizer.from_pretrained(PATH_LABELER, local_files_only=True)
model = AutoModelForSeq2SeqLM.from_pretrained(PATH_LABELER, local_files_only=True)
title_generator = pipeline("text2text-generation", model=model, tokenizer=tokenizer)

print("✅ Models Ready!\n")

# ==========================================
# 2. LOGIC FUNCTIONS
# ==========================================

def normalize_arabic(text):
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    text = re.sub(r'[أإآ]', 'ا', text)
    text = re.sub(r'ـ', '', text)
    return text

def split_text_semantically(text, threshold=0.35):
    sentences = re.split(r'[.؟!]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences: return []
    
    # Vectorize
    norm_sentences = [normalize_arabic(s) for s in sentences]
    embeddings = embedder.encode(norm_sentences)
    
    chunks = []
    current_chunk = [sentences[0]]
    
    for i in range(len(sentences) - 1):
        score = cosine_similarity([embeddings[i]], [embeddings[i+1]])[0][0]
        if score >= threshold:
            current_chunk.append(sentences[i+1])
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentences[i+1]]
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def generate_title(chunk_text):
    try:
        # Generate concise title
        result = title_generator(chunk_text, max_length=20, min_length=2, do_sample=False)
        return result[0]['generated_text']
    except:
        return "عنوان عام"

# ==========================================
# 3. MAIN JSON PROCESSING
# ==========================================

def process_dataset(input_file="input.json", output_file="output.json"):
    # 1. Read Input
    if not os.path.exists(input_file):
        print(f"❌ Error: '{input_file}' not found. Please create it first.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"📂 Processing {len(data)} records from '{input_file}'...")
    final_output = []

    # 2. Process Each Record
    for item in data:
        record_id = item.get('id', 'unknown')
        text = item.get('full_text', '')
        
        print(f"   -> Processing ID {record_id}...")
        
        # A. Split
        chunks = split_text_semantically(text)
        
        # B. Label
        topics = []
        for chunk in chunks:
            title = generate_title(chunk)
            topics.append({
                "topic": title,
                "content": chunk
            })
            
        # C. Save Structure
        final_output.append({
            "id": record_id,
            "original_text": text,
            "extracted_topics": topics
        })

    # 3. Write Output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ Done! Check '{output_file}' for results.")

if __name__ == "__main__":
    process_dataset()

# ==========================================
# 4. GEMINI AGENT TOOLS (for agentic architecture)
# ==========================================

# Define Gemini function calling tools for Text Processing Agent
CUTTER_TOOLS = [
    {
        "function_declarations": [
            {
                "name": "normalize_arabic_text",
                "description": "Normalizes Arabic text by removing diacritics, normalizing alef variants, and cleaning up the text",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The Arabic text to normalize"
                        }
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "split_text_semantic",
                "description": "Splits Arabic text into semantic chunks based on cosine similarity between sentence embeddings",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The Arabic text to split into chunks"
                        },
                        "threshold": {
                            "type": "number",
                            "description": "Similarity threshold for grouping sentences (default: 0.35)",
                            "default": 0.35
                        }
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "generate_content_title",
                "description": "Generates a concise Arabic title for the given content chunk using AraT5 model",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The Arabic content to generate a title for"
                        }
                    },
                    "required": ["content"]
                }
            }
        ]
    }
]

def execute_cutter_tool(tool_name, args):
    """
    Execute a text processing tool based on Gemini function call
    
    Args:
        tool_name: Name of the tool to execute
        args: Dictionary of arguments for the tool
    
    Returns:
        Tool execution result
    """
    try:
        if tool_name == "normalize_arabic_text":
            text = args.get("text", "")
            result = normalize_arabic(text)
            return {"normalized_text": result, "success": True}
        
        elif tool_name == "split_text_semantic":
            text = args.get("text", "")
            threshold = args.get("threshold", 0.35)
            chunks = split_text_semantically(text, threshold)
            return {
                "chunks": chunks,
                "num_chunks": len(chunks),
                "success": True
            }
        
        elif tool_name == "generate_content_title":
            content = args.get("content", "")
            title = generate_title(content)
            return {"title": title, "success": True}
        
        else:
            return {"error": f"Unknown tool: {tool_name}", "success": False}
    
    except Exception as e:
        return {"error": str(e), "success": False}
