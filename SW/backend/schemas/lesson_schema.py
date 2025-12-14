from typing import Optional
from pydantic import BaseModel

class LessonRead(BaseModel):
    id: int
    title: str
    number: str
    progress: int
    status: str
    description: Optional[str] = None

    class Config:
        orm_mode = True
