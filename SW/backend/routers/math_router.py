from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db.database import get_session
from services.math_ai_service import MathAIService
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/math", tags=["Math Tutor"])

class SubmitAnswer(BaseModel):
    student_id: int
    answer: float
    correct_answer: float

@router.get("/session/{student_id}")
async def get_math_session(student_id: int):
    mastery = MathAIService.get_or_create_mastery(student_id)
    return mastery

@router.get("/next/{student_id}")
async def get_next_problem(student_id: int):
    mastery = MathAIService.get_or_create_mastery(student_id)
    node = MathAIService.select_next_node(mastery)
    problem = MathAIService.generate_problem(node)
    return {
        "problem": problem,
        "mastery": mastery
    }

@router.post("/submit")
async def submit_math_answer(data: SubmitAnswer):
    success = (data.answer == data.correct_answer)
    updated_mastery = MathAIService.process_result(data.student_id, success)
    
    if not updated_mastery:
        raise HTTPException(status_code=404, detail="Student mastery records not found")
        
    return {
        "success": success,
        "updated_mastery": updated_mastery,
        "feedback": " ✨ برافو عليك" if success else "حاول مرة تانية يلا"
    }
@router.post("/reset/{student_id}")
async def reset_math_session(student_id: int):
    mastery = MathAIService.reset_mastery(student_id)
    if not mastery:
        raise HTTPException(status_code=404, detail="Mastery record not found")
    return mastery
