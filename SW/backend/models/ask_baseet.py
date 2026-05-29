from typing import Optional
from sqlmodel import SQLModel, Field


class AskBaseet(SQLModel, table=True):
    __tablename__ = "ask_baseet"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    
    question: str
    answer: Optional[str] = None
    context: Optional[str] = None  # Additional context for the question
    created_at: Optional[str] = None  # ISO format datetime string
    answered_at: Optional[str] = None  # ISO format datetime string

