from typing import Optional
from sqlmodel import SQLModel

class CourseBase(SQLModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class CourseRead(CourseBase):
    id: int

class CourseCreate(CourseBase):
    pass
