from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.classroom import Classroom

class ClassLevel(SQLModel, table=True):
    __tablename__ = "class_levels"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # e.g. "Level 1", "Grade 4"
    teacher_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)

    classrooms: List["Classroom"] = Relationship(back_populates="level")
