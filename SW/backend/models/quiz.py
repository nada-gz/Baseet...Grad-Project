from typing import Optional
from sqlmodel import SQLModel, Field


class Quiz(SQLModel, table=True):
    __tablename__ = "quizzes"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    
    title: str
    description: Optional[str] = None
    lesson_id: Optional[int] = None  # Optional link to a specific lesson
    status: str = "not_started"  # not_started | in_progress | completed
    score: Optional[float] = None  # Final score (0-100)
    attempts_used: int = 0
    attempts_allowed: int = 3
    questions: Optional[str] = None  # JSON string of questions
    answers: Optional[str] = None  # JSON string of student answers
    completed_at: Optional[str] = None  # ISO format datetime string
    created_at: Optional[str] = None  # ISO format datetime string

