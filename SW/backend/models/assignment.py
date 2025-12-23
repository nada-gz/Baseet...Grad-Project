from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.lesson import Lesson


class Assignment(SQLModel, table=True):
    __tablename__ = "assignments"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lessons.id")

    title: str
    description: Optional[str] = None

    # pdf | docx | img | zip | link
    assignment_type: str

    file_url: str

    # Relationship
    lesson: Optional["Lesson"] = Relationship(back_populates="assignments")
