from typing import Optional
from pydantic import BaseModel


class LessonRead(BaseModel):
    id: int
    student_id: int
    milestone_id: Optional[int] = None
    title: str
    number: str
    progress: int
    status: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


# used for resetting / updating lesson progress
class LessonUpdate(BaseModel):
    progress: int | None = None
    status: str | None = None
