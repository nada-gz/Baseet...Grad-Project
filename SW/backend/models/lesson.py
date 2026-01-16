from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.material import Material
    from models.assignment import Assignment
    from models.log import Log
    from models.milestone import Milestone


class Lesson(SQLModel, table=True):
    __tablename__ = "lessons"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")

    milestone_id: Optional[int] = Field(default=None, foreign_key="milestones.id")
    lesson_number: int

    title: str
    description: Optional[str] = None
    
    milestone: Optional["Milestone"] = Relationship()

    @property
    def milestone_number(self) -> int:
        return self.milestone.number if self.milestone else 0

    progress: int = 0
    status: str = "locked"

    materials: List["Material"] = Relationship(back_populates="lesson")
    assignments: List["Assignment"] = Relationship(back_populates="lesson")
    logs: List["Log"] = Relationship(back_populates="lesson")
