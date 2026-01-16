from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.lesson import Lesson
    from models.submission import Submission
    from models.content_assignment import ContentAssignment


class Assignment(SQLModel, table=True):
    __tablename__ = "assignments"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lessons.id")
    content_assignment_id: Optional[int] = Field(default=None, foreign_key="content_assignments.id")

    title: Optional[str] = None
    description: Optional[str] = None
    assignment_type: Optional[str] = "unknown"
    file_url: Optional[str] = ""

    deadline: Optional[datetime] = None
    
    content_assignment: Optional["ContentAssignment"] = Relationship()
    lesson: Optional["Lesson"] = Relationship(back_populates="assignments")
    submissions: List["Submission"] = Relationship(back_populates="assignment")
