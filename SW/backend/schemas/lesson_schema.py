from typing import Optional
from pydantic import BaseModel

class LessonCreate(BaseModel):
    title: str
    number: str
    status: str
    progress: int = 0
    description: Optional[str] = None

class LessonRead(BaseModel):
    id: int
    student_id: int
    title: str
    number: str
    progress: int
    status: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

