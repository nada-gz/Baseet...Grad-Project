from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.lesson import Lesson
    from models.submission import Submission


class Assignment(SQLModel, table=True):
    __tablename__ = "assignments"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lessons.id")

    title: str
    description: Optional[str] = None
    assignment_type: str = "unknown"
    file_url: str = ""

    deadline: Optional[datetime] = None

    lesson: Optional["Lesson"] = Relationship(back_populates="assignments")
    submissions: List["Submission"] = Relationship(back_populates="assignment")
