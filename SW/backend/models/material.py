from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.lesson import Lesson


class Material(SQLModel, table=True):
    __tablename__ = "materials"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lessons.id")

    title: str
    description: Optional[str] = None

    # word | pdf | ppt | img | video | audio
    material_type: str

    file_url: str

    # Relationship
    lesson: Optional["Lesson"] = Relationship(back_populates="materials")
