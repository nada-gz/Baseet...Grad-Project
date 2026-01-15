from typing import Optional
from sqlmodel import SQLModel, Field

class ContentCourse(SQLModel, table=True):
    __tablename__ = "content_courses"

    id: Optional[int] = Field(default=None, primary_key=True)
    course_number: int = Field(index=True, unique=True)
    description: Optional[str] = None
