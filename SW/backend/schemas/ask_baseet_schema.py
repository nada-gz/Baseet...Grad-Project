from typing import Optional
from pydantic import BaseModel


class AskBaseetCreate(BaseModel):
    student_id: int
    question: str
    context: Optional[str] = None


class AskBaseetRead(BaseModel):
    id: int
    student_id: int
    question: str
    answer: Optional[str] = None
    context: Optional[str] = None
    created_at: Optional[str] = None
    answered_at: Optional[str] = None

    class Config:
        from_attributes = True


class AskBaseetUpdate(BaseModel):
    answer: Optional[str] = None
    answered_at: Optional[str] = None

