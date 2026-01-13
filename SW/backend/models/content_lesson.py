from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.content_material import ContentMaterial


class ContentLesson(SQLModel, table=True):
    __tablename__ = "content_lessons"

    id: Optional[int] = Field(default=None, primary_key=True)

    level_number: int
    milestone_number: int
    lesson_number: int

    title: str
    description: Optional[str] = None

    materials: List["ContentMaterial"] = Relationship(back_populates="lesson")
