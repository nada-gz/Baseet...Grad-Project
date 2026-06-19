"""
test_qwen_migration.py
Manual + automated smoke tests for the Gemini -> Qwen (DashScope) migration.
Run: python test_qwen_migration.py
"""

import os
import sys
import traceback

# Ensure the service directory is on sys.path so the local explanation module imports correctly.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# ---- ADJUST THIS to match your actual module filename ----
import explanation as backend
# ------------------------------------------------------------

PASS = "✅"
FAIL = "❌"
WARN = "⚠️"

# Heuristic persona markers to sanity-check tone (not strict — just a flag for manual review)
PERSONA_MARKERS = ["يلا", "تمام", "كده", "برافو", "بص", "شايف", "صح", "احنا"]

results = []


def record(name, ok, note=""):
    results.append((name, ok, note))
    tag = PASS if ok else FAIL
    print(f"{tag} {name}" + (f" — {note}" if note else ""))


def check_persona_markers(text):
    hits = [m for m in PERSONA_MARKERS if m in text]
    return hits


# ----------------------------------------------------------------------
# 1. Environment / client sanity
# ----------------------------------------------------------------------
def test_env_and_client():
    try:
        key = os.getenv("DASHSCOPE_API_KEY")
        assert key, "DASHSCOPE_API_KEY not set in environment / .env"
        client = backend.get_qwen_client()
        record("Env var + client init", True)
        return client
    except Exception as e:
        record("Env var + client init", False, str(e))
        traceback.print_exc()
        return None


# ----------------------------------------------------------------------
# 2. Raw completion call (no persona, just connectivity)
# ----------------------------------------------------------------------
def test_raw_completion(client):
    try:
        response = client.chat.completions.create(
            model=backend.GENERATION_MODEL,
            messages=[{"role": "user", "content": "قول 'تمام' فقط ولا تقول حاجة تانية."}],
        )
        text = response.choices[0].message.content.strip()
        ok = len(text) > 0
        record("Raw DashScope completion", ok, f"reply: {text[:60]!r}")
    except Exception as e:
        record("Raw DashScope completion", False, str(e))
        traceback.print_exc()


# ----------------------------------------------------------------------
# 3. Persona system instruction sanity
# ----------------------------------------------------------------------
def test_system_instruction():
    try:
        sys_instr = backend.prepare_system_instruction()
        ok = "يلا" in sys_instr and "ملناش دعوة" in sys_instr
        record("Persona blueprint present in system instruction", ok)
        return sys_instr
    except Exception as e:
        record("Persona blueprint present in system instruction", False, str(e))
        traceback.print_exc()
        return None


# ----------------------------------------------------------------------
# 4. Chat session: new question -> persona-voiced answer
# ----------------------------------------------------------------------
def test_chat_new_question(client, sys_instr):
    try:
        chat = backend.initialize_chat_session(client, sys_instr)
        context = "الشمس نجم كبير جدًا في وسط مجموعتنا الشمسية، وهي مصدر الضوء والحرارة للأرض."
        answer = backend.generate_rag_answer_with_chat(
            chat, query_text="اي هي الشمس و ليه موجوده؟", context_string=context, is_clarification=False
        )
        hits = check_persona_markers(answer)
        ok = len(answer) > 0 and not answer.startswith("❌")
        record("Chat: new question", ok, f"persona markers found: {hits}")
        print("   --- FULL RESPONSE (manual review) ---")
        print("  ", answer.replace("\n", "\n   "))
        print("   --------------------------------------")
        return chat
    except Exception as e:
        record("Chat: new question", False, str(e))
        traceback.print_exc()
        return None


# ----------------------------------------------------------------------
# 5. Chat session: clarification turn -> must NOT repeat previous answer
# ----------------------------------------------------------------------
def test_chat_clarification(chat):
    if chat is None:
        record("Chat: clarification", False, "skipped, prior chat session failed")
        return
    try:
        context = "الشمس نجم كبير جدًا في وسط مجموعتنا الشمسية، وهي مصدر الضوء والحرارة للأرض."
        answer = backend.generate_rag_answer_with_chat(
            chat, query_text="مش فاهم", context_string=context, is_clarification=True
        )
        ok = len(answer) > 0 and not answer.startswith("❌")
        record("Chat: clarification turn", ok)
        print("   --- FULL RESPONSE (manual review) ---")
        print("  ", answer.replace("\n", "\n   "))
        print("   --------------------------------------")
    except Exception as e:
        record("Chat: clarification turn", False, str(e))
        traceback.print_exc()


# ----------------------------------------------------------------------
# 6. Single MCQ generation
# ----------------------------------------------------------------------
def test_mcq(client):
    try:
        context = "القمر يدور حول الأرض، وهو سبب حدوث المد والجزر في البحار."
        mcq = backend.generate_mcq(client, context)
        ok = (
            mcq is not None
            and "question_ar" in mcq
            and "options_ar" in mcq
            and len(mcq["options_ar"]) == 3
            and mcq.get("correct_answer_ar") is not None
        )
        record("MCQ generation (schema check)", ok, str(mcq)[:120] if mcq else "None returned")
        return mcq
    except Exception as e:
        record("MCQ generation (schema check)", False, str(e))
        traceback.print_exc()
        return None


# ----------------------------------------------------------------------
# 7. Batch MCQ generation + duplicate-avoidance
# ----------------------------------------------------------------------
def test_batch_mcq(client, prev_mcq):
    try:
        context = "القمر يدور حول الأرض، وهو سبب حدوث المد والجزر في البحار."
        prev_questions = [prev_mcq["question_ar"]] if prev_mcq else None
        batch = backend.generate_batch_mcqs(client, context, count=2, previous_questions=prev_questions)
        ok = isinstance(batch, list) and len(batch) >= 1
        record("Batch MCQ generation", ok, f"{len(batch) if isinstance(batch, list) else 0} questions returned")

        if prev_mcq and batch:
            dup = any(q.get("question_ar") == prev_mcq["question_ar"] for q in batch)
            record("Batch MCQ avoids duplicate of prior question", not dup)
    except Exception as e:
        record("Batch MCQ generation", False, str(e))
        traceback.print_exc()


# ----------------------------------------------------------------------
# 8. ChromaDB retrieval (optional — skips cleanly if DB not built yet)
# ----------------------------------------------------------------------
def test_retrieval():
    try:
        import chromadb
        chroma_client = chromadb.PersistentClient(path=backend.CHROMA_DB_PATH)
        embed_model = backend.setup_retrieval_model()
        results_ = backend.get_context_from_db(chroma_client, "الشمس", embed_model, k=3)
        ok = isinstance(results_, list)
        record("ChromaDB retrieval", ok, f"{len(results_)} chunks returned")
    except Exception as e:
        record("ChromaDB retrieval", False, f"skipped/failed: {e}")


# ----------------------------------------------------------------------
# Runner
# ----------------------------------------------------------------------
def main():
    print("=" * 60)
    print("QWEN MIGRATION TEST SUITE")
    print("=" * 60)

    client = test_env_and_client()
    if client is None:
        print("\nAborting further tests — client failed to initialize.")
        sys.exit(1)

    test_raw_completion(client)
    sys_instr = test_system_instruction()
    chat = test_chat_new_question(client, sys_instr)
    test_chat_clarification(chat)
    mcq = test_mcq(client)
    test_batch_mcq(client, mcq)
    test_retrieval()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    for name, ok, note in results:
        print(f"{PASS if ok else FAIL} {name}")
    print(f"\n{passed}/{total} checks passed.")
    if passed < total:
        print(f"{WARN} Review the FULL RESPONSE blocks above manually — persona/tone correctness isn't fully automatable.")


if __name__ == "__main__":
    main()