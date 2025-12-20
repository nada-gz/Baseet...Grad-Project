from typing import Optional
from sqlmodel import SQLModel, Field


class Lesson(SQLModel, table=True):
    __tablename__ = "lessons"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")

    milestone_number: int
    lesson_number: int

    title: str
    description: Optional[str] = None

    progress: int = 0
    status: str = "locked"
