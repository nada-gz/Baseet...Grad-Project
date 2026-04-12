from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.content_material import ContentMaterial
    from models.content_assignment import ContentAssignment


class ContentLesson(SQLModel, table=True):
    __tablename__ = "content_lessons"

    id: Optional[int] = Field(default=None, primary_key=True)

    course_number: int
    milestone_number: int
    lesson_number: int

    title: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(default=20)
    teacher_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)

    materials: List["ContentMaterial"] = Relationship(back_populates="lesson")
    assignments: List["ContentAssignment"] = Relationship(back_populates="lesson")
