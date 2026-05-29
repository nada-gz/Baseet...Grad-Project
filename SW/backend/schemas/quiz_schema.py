from typing import Optional
from pydantic import BaseModel


class QuizCreate(BaseModel):
    student_id: int
    title: str
    description: Optional[str] = None
    lesson_id: Optional[int] = None
    attempts_allowed: int = 3
    questions: Optional[str] = None


class QuizRead(BaseModel):
    id: int
    student_id: int
    title: str
    description: Optional[str] = None
    lesson_id: Optional[int] = None
    status: str
    score: Optional[float] = None
    attempts_used: int
    attempts_allowed: int
    questions: Optional[str] = None
    answers: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    score: Optional[float] = None
    attempts_used: Optional[int] = None
    answers: Optional[str] = None
    completed_at: Optional[str] = None

