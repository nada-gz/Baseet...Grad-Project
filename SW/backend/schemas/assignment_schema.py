from typing import Optional
from pydantic import BaseModel 


class AssignmentCreate(BaseModel):
    student_id: int
    title: str
    description: Optional[str] = None
    lesson_id: Optional[int] = None
    due_date: Optional[str] = None


class AssignmentRead(BaseModel):
    id: int
    student_id: int
    title: str
    description: Optional[str] = None
    lesson_id: Optional[int] = None
    status: str
    submission_url: Optional[str] = None
    grade: Optional[float] = None
    feedback: Optional[str] = None
    due_date: Optional[str] = None
    submitted_at: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    submission_url: Optional[str] = None
    grade: Optional[float] = None
    feedback: Optional[str] = None
    submitted_at: Optional[str] = None

