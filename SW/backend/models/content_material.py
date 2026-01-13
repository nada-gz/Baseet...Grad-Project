from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.content_lesson import ContentLesson


class ContentMaterial(SQLModel, table=True):
    __tablename__ = "content_materials"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="content_lessons.id")

    title: str
    file_url: str
    material_type: str

    lesson: "ContentLesson" = Relationship(back_populates="materials")
