from typing import Optional
from sqlmodel import SQLModel, Field


class Assignment(SQLModel, table=True):
    __tablename__ = "assignments"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    
    title: str
    description: Optional[str] = None
    lesson_id: Optional[int] = None  # Optional link to a specific lesson
    status: str = "pending"  # pending | submitted | graded
    submission_url: Optional[str] = None  # URL to student's submission
    grade: Optional[float] = None
    feedback: Optional[str] = None
    due_date: Optional[str] = None  # ISO format datetime string
    submitted_at: Optional[str] = None  # ISO format datetime string
    created_at: Optional[str] = None  # ISO format datetime string

