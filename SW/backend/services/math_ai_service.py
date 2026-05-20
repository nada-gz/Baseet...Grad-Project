from sqlmodel import Session, select
from db.database import engine
from models.student_math_mastery import StudentMathMastery
import random
from datetime import datetime

# Node Order (Hierarchy from easiest to hardest)
NODE_ORDER = [
    "subitizing",
    "number_line",
    "place_value",
    "fact_retrieval",
    "word_problems"
]

class MathAIService:
    @staticmethod
    def get_or_create_mastery(student_id: int):
        with Session(engine) as session:
            mastery = session.exec(
                select(StudentMathMastery).where(StudentMathMastery.student_id == student_id)
            ).first()
            if not mastery:
                mastery = StudentMathMastery(student_id=student_id)
                session.add(mastery)
                session.commit()
                session.refresh(mastery)
            return mastery

    @staticmethod
    def select_next_node(mastery: StudentMathMastery):
        # Logic: If mastery > 0.8 on current node, attempt next node.
        # If consecutive_errors >= 2, drop to previous node.
        
        current_idx = NODE_ORDER.index(mastery.current_node)
        changed = False
        
        if mastery.consecutive_errors >= 2:
            # Scale down
            new_idx = max(0, current_idx - 1)
            if mastery.current_node != NODE_ORDER[new_idx]:
                mastery.current_node = NODE_ORDER[new_idx]
                changed = True
            mastery.consecutive_errors = 0 # Reset always
            
        current_mastery_val = getattr(mastery, mastery.current_node)
        if current_mastery_val > 0.8 and current_idx < len(NODE_ORDER) - 1:
            # Scale up
            mastery.current_node = NODE_ORDER[current_idx + 1]
            changed = True
            
        if changed:
            with Session(engine) as session:
                session.add(mastery)
                session.commit()
                session.refresh(mastery)
                
        return mastery.current_node

    @staticmethod
    def generate_problem(node: str):
        if node == "subitizing":
            num = random.randint(1, 6)
            return {
                "type": "subitizing",
                "question": "شايف كام مكعب قدامك؟",
                "data": {"count": num},
                "answer": num,
                "hint": "عدهم واحد واحد يا بطل ✨",
                "mode": "manipulatives"
            }
        elif node == "number_line":
            target = random.randint(1, 15)
            return {
                "type": "number_line",
                "question": f"حط المؤشر عند رقم {target}",
                "data": {"target": target, "range": [0, 15]},
                "answer": target,
                "hint": "دور على الرقم على الخط وروح عنده",
                "mode": "number_line"
            }
        elif node == "place_value":
            num = random.randint(11, 20)
            tens = 10
            ones = num - 10
            return {
                "type": "place_value",
                "question": f"إزاي نكون رقم {num}؟",
                "data": {"total": num, "options": [tens, ones]},
                "answer": ones,
                "hint": f"رقم {num} عبارة عن عشرة وكام كمان؟",
                "mode": "place_value"
            }
        elif node == "fact_retrieval":
            a = random.randint(1, 5)
            b = random.randint(1, 5)
            return {
                "type": "fact_retrieval",
                "question": f"هيبقى كام لما نجمع {a} + {b}؟",
                "data": {"a": a, "b": b, "op": "+"},
                "answer": a + b,
                "hint": "جرب تجمعهم كلهم مع بعض",
                "mode": "equation"
            }
        else: # word_problems
            names = ["بسيط", "سامي", "سارة"]
            items = ["تفاحات", "نجوم", "مكعبات"]
            name = random.choice(names)
            item = random.choice(items)
            a = random.randint(1, 3)
            b = random.randint(1, 2)
            return {
                "type": "word_problems",
                "question": f"{name} معاه {a} {item}.. وأخد {b} كمان.. يبقى معاه كام دلوقتي؟",
                "data": {"a": a, "b": b, "context": f"{name} & {item}"},
                "answer": a + b,
                "hint": "الكل بيساوي اللي كان معاه + الزيادة",
                "mode": "word_problem"
            }

    @staticmethod
    def process_result(student_id: int, success: bool):
        with Session(engine) as session:
            mastery = session.exec(
                select(StudentMathMastery).where(StudentMathMastery.student_id == student_id)
            ).first()
            
            if not mastery:
                return None

            current_val = getattr(mastery, mastery.current_node)
            
            if success:
                # Bayesian-lite update: Increase probability
                new_val = min(1.0, current_val + 0.25)
                setattr(mastery, mastery.current_node, new_val)
                mastery.consecutive_errors = 0
            else:
                # Decrease probability
                new_val = max(0.0, current_val - 0.1)
                setattr(mastery, mastery.current_node, new_val)
                mastery.consecutive_errors += 1

            mastery.last_updated = datetime.now().isoformat()
            session.add(mastery)
            session.commit()
            session.refresh(mastery)
            return mastery

    @staticmethod
    def reset_mastery(student_id: int):
        with Session(engine) as session:
            mastery = session.exec(
                select(StudentMathMastery).where(StudentMathMastery.student_id == student_id)
            ).first()
            if mastery:
                mastery.current_node = NODE_ORDER[0]
                mastery.consecutive_errors = 0
                for node in NODE_ORDER:
                    setattr(mastery, node, 0.0)
                mastery.last_updated = datetime.now().isoformat()
                session.add(mastery)
                session.commit()
                session.refresh(mastery)
            return mastery
