from typing import Optional
from pydantic import BaseModel


class LessonRead(BaseModel):
    id: int
    student_id: int

    milestone_number: int
    lesson_number: int

    title: str
    description: Optional[str] = None

    progress: int
    status: str

    number: str

    class Config:
        orm_mode = True


# used for resetting / updating lesson progress
class LessonUpdate(BaseModel):
    progress: Optional[int] = None
    status: Optional[str] = None
