from typing import Optional
from sqlmodel import SQLModel, Field


class Milestone(SQLModel, table=True):
    __tablename__ = "milestones"

    id: Optional[int] = Field(default=None, primary_key=True)

    student_id: int = Field(foreign_key="students.id")

    course_id: Optional[int] = Field(default=None, foreign_key="courses.id")
    title: str
    number: int   # milestone number (1, 2, 3, ...)
    description: Optional[str] = None
