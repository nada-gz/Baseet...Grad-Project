from typing import Optional
from pydantic import BaseModel

class LessonCreate(BaseModel):
    milestone_id: int
    title: str
    lesson_code: str  # e.g., "1.1", "1.2", "2.1"
    order: int
    status: str
    progress: int = 0
    description: Optional[str] = None
    content_url: Optional[str] = None

class LessonRead(BaseModel):
    id: int
    student_id: int
    milestone_id: int
    title: str
    lesson_code: str
    order: int
    progress: int
    status: str
    description: Optional[str] = None
    content_url: Optional[str] = None

    class Config:
        from_attributes = True

