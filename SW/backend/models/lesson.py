from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.material import Material
    from models.assignment import Assignment


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

    materials: List["Material"] = Relationship(back_populates="lesson")
    assignments: List["Assignment"] = Relationship(back_populates="lesson")
