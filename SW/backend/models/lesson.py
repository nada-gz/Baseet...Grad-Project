from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Lesson(SQLModel, table=True):
    __tablename__ = "lessons"

    id: Optional[int] = Field(default=None, primary_key=True)

    student_id: int = Field(foreign_key="students.id")
    milestone_id: int = Field(foreign_key="milestones.id")

    title: str
    lesson_code: str  # e.g. "1.1", "1.2", "2.1" (replaces number)
    order: int  # Order within the milestone
    progress: int = 0  # 0 → 100
    status: str  # locked | in-progress | completed
    description: Optional[str] = None
    content_url: Optional[str] = None  # URL or path to lesson content
    
    # Relationship to milestone
    milestone: "Milestone" = Relationship(back_populates="lessons")


from .milestone import Milestone

